"""
Сервис интеграции с Яндекс Документами через протокол WOPI.

Обеспечивает чтение и запись посещаемости в таблицу .xlsx на Яндекс Диске.
Поскольку прямая публичная веб-ссылка docs.yandex.ru защищена капчей,
сессионный токен доступа WOPI извлекается через headless Chromium.
Запись в файл выполняется по стандарту WOPI (HTTP POST с X-WOPI-Override: PUT)
с соблюдением активной блокировки X-WOPI-Lock.
"""

import asyncio
import html
import io
import json
import re
import uuid
import zipfile
from datetime import date, datetime

import defusedxml.ElementTree as ET
import httpx
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from config import ATTENDANCE_DOC_URL, REDIS_COOKIE_TTL_SECONDS, REDIS_YANDEX_COOKIE_KEY
from core.logger import get_logger

log = get_logger("yandex_docs")

# Соответствие порядкового номера месяца короткому имени вкладки
MONTH_SHEET_MAP: dict[int, str] = {
    1: "ЯНВ",
    2: "ФЕВР",
    3: "МАРТ",
    4: "АПР",
    5: "МАЙ",
    6: "ИЮН",
    7: "ИЮЛ",
    8: "АВГ",
    9: "СЕНТ",
    10: "ОКТ",
    11: "НОЯБ",
    12: "ДЕК",
}


class WopiSession:
    """
    Сессия авторизованного доступа к документу по протоколу WOPI.

    resource_url: Базовый URL документа в WOPI сервисе Яндекса.
    access_token: Временный токен с правами на запись (UserCanWrite=True).
    lock_id: Идентификатор активной сессионной блокировки редактора.
    """

    def __init__(self, resource_url: str, access_token: str, lock_id: str):
        # resource_url — базовый URL документа в WOPI сервисе Яндекса
        # access_token — временный токен с правами на запись (UserCanWrite=True)
        # lock_id — идентификатор активной сессионной блокировки редактора
        self.resource_url = resource_url
        self.access_token = access_token
        self.lock_id = lock_id


def extract_client_config(html_content: str) -> dict:
    """
    Извлекает JSON конфигурации редактора из HTML-разметки страницы документа.

    Парсит блок <script id="client-config"> и верифицирует, не была ли сессия
    перенаправлена на страницу авторизации Яндекс ID.

    Возвращает словарь параметров сессии или выбрасывает ValueError при истечении куки.
    """
    match = re.search(r'<script[^>]*id="client-config"[^>]*>(.*?)</script>', html_content)
    if match:
        return json.loads(match.group(1))
    if "<title>Авторизация</title>" in html_content or "passp-bg" in html_content:
        raise ValueError("Сессия Яндекс Документов истекла (страница авторизации). Обновите YANDEX_COOKIE в .env")
    raise ValueError("Тег client-config не найден в DOM Яндекс Документов")


def merge_cookie_header(current_cookie: str, new_cookies: dict[str, str]) -> str:
    """
    Объединяет текущую строку заголовка Cookie со свежими токенами из Set-Cookie.

    Парсит пары ключ-значение и перезаписывает изменившиеся токены сессии,
    сохраняя неизмененные куки авторизации.

    Возвращает объединенную строку формата 'key=value; key2=value2'.
    """
    cookie_map = {}
    for part in current_cookie.split(";"):
        if "=" in part:
            k, v = part.strip().split("=", 1)
            cookie_map[k] = v
    for k, v in new_cookies.items():
        cookie_map[k] = v
    return "; ".join(f"{k}={v}" for k, v in cookie_map.items())


def get_yandex_cookie_header() -> str:
    """
    Формирует резервную строку Cookie из статических переменных окружения.

    Использует YANDEX_COOKIE или одиночный YANDEX_SESSION_ID при отсутствии
    актуальных куки в оперативной памяти Redis.

    Возвращает форматированную строку Cookie или пустую строку.
    """
    from config import YANDEX_COOKIE, YANDEX_SESSION_ID

    if YANDEX_COOKIE:
        return YANDEX_COOKIE.strip()
    if YANDEX_SESSION_ID:
        return f"Session_id={YANDEX_SESSION_ID.strip()}"
    return ""


async def get_effective_yandex_cookie() -> str:
    """
    Предоставляет наиболее свежие Cookie сессии с приоритетом чтения из Redis.

    Позволяет динамически обновлять сессию без перезапуска сервисов para-api и para-worker,
    переходя на .env только при пустом кэше.

    Возвращает актуальную строку заголовка Cookie для сетевых вызовов.
    """
    try:
        from core.redis import get_redis

        r = await get_redis()
        if r:
            cached = await r.get(REDIS_YANDEX_COOKIE_KEY)
            if cached:
                return cached
    except Exception as e:
        log.warning("Не удалось прочитать Cookie из Redis: %s", e)
    return get_yandex_cookie_header()


async def save_effective_yandex_cookie(cookie_str: str) -> None:
    """
    Атомарно сохраняет актуальную строку Cookie в постоянный кэш Redis с TTL.

    Продлевает срок жизни кэшированной сессии на 60 дней, обеспечивая непрерывную
    синхронизацию между всеми контейнерами системы.

    Не возвращает значений; логирует результат на уровне debug.
    """
    try:
        from core.redis import get_redis

        r = await get_redis()
        if r and cookie_str:
            await r.set(REDIS_YANDEX_COOKIE_KEY, cookie_str, ex=REDIS_COOKIE_TTL_SECONDS)
            log.debug("Актуальные Cookie Яндекс Документов обновлены в Redis")
    except Exception as e:
        log.warning("Не удалось сохранить Cookie в Redis: %s", e)


async def update_cookies_from_response(res: httpx.Response, current_cookie: str) -> None:
    """
    Извлекает полученные от сервера Set-Cookie и синхронизирует их с Redis.

    Предотвращает устаревание сессионных меток Паспорта при плановой ротации токенов
    на стороне облачной инфраструктуры Яндекса.

    Не возвращает значений; инициирует асинхронную запись при наличии изменений.
    """
    if not res.cookies:
        return
    new_cookies = dict(res.cookies)
    merged = merge_cookie_header(current_cookie, new_cookies)
    if merged != current_cookie:
        await save_effective_yandex_cookie(merged)


def _build_dom_headers(cookie_hdr: str) -> dict[str, str]:
    """
    Формирует заголовки браузерного эмулятора для загрузки страницы документа.

    Подставляет реалистичный User-Agent и языковые настройки для минимизации
    риска получения веб-капчи от антифрод-системы Яндекс.

    Возвращает словарь HTTP-заголовков запроса.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru,en;q=0.9",
    }
    if cookie_hdr:
        headers["Cookie"] = cookie_hdr
    return headers


async def fetch_page_dom(doc_url: str) -> str:
    """
    Загружает исходный HTML-код страницы веб-редактора Яндекс Документов.

    Использует защищенные заголовки и куки авторизации, автоматически перехватывая
    и сохраняя обновленные Set-Cookie из ответа.

    Возвращает полный текст HTML страницы или выбрасывает RuntimeError.
    """
    cookie_hdr = await get_effective_yandex_cookie()
    headers = _build_dom_headers(cookie_hdr)
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        res = await client.get(doc_url, headers=headers)
        if res.status_code != 200:
            raise RuntimeError(f"Ошибка загрузки страницы документа: HTTP {res.status_code}")
        await update_cookies_from_response(res, cookie_hdr)
        return res.text


async def get_active_wopi_lock(resource_url: str, token: str) -> str:
    """
    Определяет текущий активный идентификатор блокировки файла по стандарту WOPI.

    Отправляет пустой PUT-запрос к эндпоинту документа и считывает заголовок x-wopi-lock
    из ответа с кодом 409 Conflict.

    Возвращает строку lock-идентификатора или генерирует новый UUID.
    """
    url = f"{resource_url}/contents?access_token={token}"
    headers = {"X-WOPI-Override": "PUT", "Content-Type": "application/octet-stream"}
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.post(url, headers=headers, content=b"")
        lock = res.headers.get("x-wopi-lock") or f"wopi-lock-{uuid.uuid4().hex[:8]}"
        log.debug("Получен WOPI lock: %s (HTTP %s)", lock, res.status_code)
        return lock


async def init_wopi_session(doc_url: str = ATTENDANCE_DOC_URL) -> WopiSession:
    """
    Инициализирует сессию WOPI, извлекая resource_url, access_token и lock.

    Выполняет парсинг клиентского DOM и запрашивает параметры сессии для
    последующего чтения и записи файла .xlsx.

    Возвращает валидный объект WopiSession или выбрасывает исключение.
    """
    log.debug("Инициализация WOPI сессии через Chromium...")
    html = await fetch_page_dom(doc_url)
    config = extract_client_config(html)
    action_data = config.get("officeActionData", {})
    res_url = action_data.get("resource_url")
    token = action_data.get("access_token")
    if not res_url or not token:
        raise RuntimeError("Не удалось извлечь resource_url или access_token")
    lock_id = await get_active_wopi_lock(res_url, token)
    log.info("WOPI-сессия успешно инициализирована")
    return WopiSession(res_url, token, lock_id)


def load_workbook_from_bytes(content: bytes) -> openpyxl.Workbook:
    """
    Синхронно десериализует байты книги openpyxl с подавлением предупреждений.

    Изолирует парсинг поврежденных стилей шрифтов и пустых ячеек без засорения
    системного лога предупреждениями UserWarning библиотеки openpyxl.

    Возвращает объект openpyxl.Workbook.
    """
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        return openpyxl.load_workbook(io.BytesIO(content))


def compute_sheet_summary_counts(sheet: Worksheet) -> dict[tuple[str, int], int]:
    """
    Вычисляет агрегированное количество отметок О, У, Н по строкам студентов.

    Служит источником данных для инжекции кэшированных значений формул в XML листа,
    чтобы веб-интерфейс отображал статистику без ручного пересчета.

    Возвращает словарь {(буква_колонки, номер_строки): число_отметок}.
    """
    mc = sheet.max_column
    if mc < 4:
        return {}
    c_o, c_u, c_n = mc - 2, mc - 1, mc
    l_o = openpyxl.utils.get_column_letter(c_o)
    l_u = openpyxl.utils.get_column_letter(c_u)
    l_n = openpyxl.utils.get_column_letter(c_n)
    counts = {}
    for r in range(5, 37):
        row_vals = [sheet.cell(r, c).value for c in range(3, mc - 2)]
        counts[(l_o, r)] = sum(1 for v in row_vals if v == "О")
        counts[(l_u, r)] = sum(1 for v in row_vals if v == "У")
        counts[(l_n, r)] = sum(1 for v in row_vals if v == "Н")
    return counts


def patch_sheet_xml_counts(xml_text: str, counts: dict[tuple[str, int], int]) -> str:
    """
    Заменяет кэшированные теги формул <v></v> в XML листа на вычисленные суммы.

    Обеспечивает корректное отображение итогов посещаемости в OnlyOffice и Excel Online,
    которые не вычисляют формулы COUNTIF на лету в режиме просмотра.

    Возвращает модифицированный текст XML листа книги.
    """

    def repl(m):
        col, r = m.group(1), int(m.group(2))
        if (col, r) not in counts:
            return m.group(0)
        count = counts[(col, r)]
        tag = m.group(0)
        if re.search(r"<(?:\w+:)?v[>/]", tag):
            return re.sub(r"<(?:\w+:)?v[^>]*>.*?</(?:\w+:)?v>|<(?:\w+:)?v\s*/>", f"<v>{count}</v>", tag)
        return re.sub(r"</(?:\w+:)?c>", f"<v>{count}</v></c>", tag)

    pattern = (
        r"<(?:\w+:)?c\s+r=\"([A-Z]+)(\d+)\"[^>]*>"
        r"<(?:\w+:)?f[^>]*>[^<]+</(?:\w+:)?f>"
        r"(?:<(?:\w+:)?v>[^<]*</(?:\w+:)?v>|<(?:\w+:)?v\s*/>)?"
        r"</(?:\w+:)?c>"
    )
    return re.sub(pattern, repl, xml_text)


def _write_summary_col_header(sheet: Worksheet, col: int, title: str, code: str) -> None:
    """
    Записывает текстовые заголовки и условные обозначения итоговых колонок.

    Устанавливает полное наименование категории во 2-й строке и однобуквенный
    символ в 3-й строке листа.

    Не возвращает значений; модифицирует ячейки на переданном листе.
    """
    sheet.cell(2, col, title)
    sheet.cell(3, col, code)


def _write_summary_formulas(sheet: Worksheet, mc: int, l_o: str, l_u: str, l_n: str, end_col: str) -> None:
    """
    Проставляет формулы COUNTIF для подсчета отметок по строкам 5-36.

    Формирует динамические формулы Excel с абсолютными ссылками на коды категорий
    в шапке таблицы.

    Не возвращает значений; записывает строковые формулы в ячейки.
    """
    c_o, c_u, c_n = mc - 2, mc - 1, mc
    for r in range(5, 37):
        sheet.cell(r, c_o, f"=COUNTIF($C{r}:${end_col}{r},{l_o}$3)")
        sheet.cell(r, c_u, f"=COUNTIF($C{r}:${end_col}{r},{l_u}$3)")
        sheet.cell(r, c_n, f"=COUNTIF($C{r}:${end_col}{r},{l_n}$3)")


def ensure_all_summary_headers(wb: openpyxl.Workbook) -> None:
    """
    Гарантирует наличие заголовков, кодов и формул COUNTIF во всех листах месяцев.

    Итерирует по вкладкам календаря, восстанавливая поврежденные или случайно
    удаленные итоговые столбцы таблицы посещаемости.

    Не возвращает значений; модифицирует структуру книги openpyxl in-place.
    """
    for name in wb.sheetnames:
        if name not in MONTH_SHEET_MAP.values():
            continue
        sheet = wb[name]
        mc = sheet.max_column
        if mc < 4:
            continue
        c_o, c_u, c_n = mc - 2, mc - 1, mc
        l_o, l_u, l_n = (openpyxl.utils.get_column_letter(c) for c in (c_o, c_u, c_n))
        end_col = openpyxl.utils.get_column_letter(mc - 3)
        _write_summary_col_header(sheet, c_o, "Опоздавшие", "О")
        _write_summary_col_header(sheet, c_u, "отсутствие по уважительной причине", "У")
        _write_summary_col_header(sheet, c_n, "отсутствие по неуважительной причине", "Н")
        _write_summary_formulas(sheet, mc, l_o, l_u, l_n, end_col)


def inject_summary_cache(raw_bytes: bytes, wb: openpyxl.Workbook) -> bytes:
    """
    Инжектирует предрассчитанные значения формул COUNTIF прямо в zip-архив xlsx.

    Парсит структуру zip-пакета и модифицирует XML-файлы листов sheet*.xml без
    полной десериализации всей книги.

    Возвращает обновленные бинарные байты xlsx-файла.
    """
    sheet_map = {f"xl/worksheets/sheet{i + 1}.xml": name for i, name in enumerate(wb.sheetnames)}
    in_zip = zipfile.ZipFile(io.BytesIO(raw_bytes))
    out_buf = io.BytesIO()
    with zipfile.ZipFile(out_buf, "w", zipfile.ZIP_DEFLATED) as out_zip:
        for item in in_zip.infolist():
            content = in_zip.read(item.filename)
            sh_name = sheet_map.get(item.filename)
            if sh_name and sh_name in MONTH_SHEET_MAP.values():
                counts = compute_sheet_summary_counts(wb[sh_name])
                content = patch_sheet_xml_counts(content.decode("utf-8"), counts).encode("utf-8")
            out_zip.writestr(item, content)
    return out_buf.getvalue()


def save_workbook_to_bytes(wb: openpyxl.Workbook) -> bytes:
    """
    Сериализует книгу openpyxl в бинарные байты с принудительным пересчетом формул.

    Включает флаги forceFullCalc и fullCalcOnLoad для гарантии пересчета ячеек
    при последующем открытии файла пользователем на компьютере.

    Возвращает готовый бинарный поток байтов книги Excel.
    """
    ensure_all_summary_headers(wb)
    wb.calculation.calcMode = "auto"
    wb.calculation.fullCalcOnLoad = True
    wb.calculation.forceFullCalc = True
    buf = io.BytesIO()
    wb.save(buf)
    return inject_summary_cache(buf.getvalue(), wb)


async def download_workbook(session: WopiSession) -> openpyxl.Workbook:
    """
    Скачивает актуальный контент таблицы по протоколу WOPI и возвращает объект книги.

    Выполняет HTTP GET к resource_url/contents с токеном доступа, логируя размер файла
    и десериализуя книгу в неблокирующем потоке.

    Возвращает объект openpyxl.Workbook или выбрасывает RuntimeError.
    """
    url = f"{session.resource_url}/contents?access_token={session.access_token}"
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        res = await client.get(url)
        if res.status_code != 200:
            raise RuntimeError(f"Ошибка скачивания таблицы: HTTP {res.status_code}")
        wb = await asyncio.to_thread(load_workbook_from_bytes, res.content)
        log.info("Таблица успешно скачана (%s байт)", len(res.content))
        return wb


async def acquire_wopi_lock(session: WopiSession, client: httpx.AsyncClient, lock_id: str) -> bool:
    """
    Захватывает монопольную сессионную блокировку файла по стандарту WOPI LOCK.

    Защищает от состояния гонки при параллельном редактировании таблицы несколькими
    пользователями или процессами.

    Возвращает True в случае успешного ответа HTTP 200, иначе False.
    """
    url = f"{session.resource_url}?access_token={session.access_token}"
    hdr = {"X-WOPI-Override": "LOCK", "X-WOPI-Lock": lock_id}
    res = await client.post(url, headers=hdr)
    return res.status_code == 200


async def release_wopi_lock(session: WopiSession, client: httpx.AsyncClient, lock_id: str) -> bool:
    """
    Снимает активную сессионную блокировку с файла по стандарту WOPI UNLOCK.

    Освобождает файл для доступа веб-редакторам после завершения фиксации отметок.

    Возвращает True при успешном снятии блокировки (HTTP 200), иначе False.
    """
    url = f"{session.resource_url}?access_token={session.access_token}"
    hdr = {"X-WOPI-Override": "UNLOCK", "X-WOPI-Lock": lock_id}
    res = await client.post(url, headers=hdr)
    return res.status_code == 200


async def put_wopi_contents(
    session: WopiSession, client: httpx.AsyncClient, data: bytes, lock_id: str
) -> httpx.Response:
    """
    Выполняет HTTP POST-запрос с заголовком X-WOPI-Override: PUT для перезаписи файла.

    Передает бинарное тело таблицы с обязательным заголовком активной блокировки X-WOPI-Lock.

    Возвращает объект httpx.Response с ответом сервера Яндекса.
    """
    url = f"{session.resource_url}/contents?access_token={session.access_token}"
    hdr = {
        "X-WOPI-Override": "PUT",
        "Content-Type": "application/octet-stream",
        "X-WOPI-Lock": lock_id,
    }
    res = await client.post(url, headers=hdr, content=data)
    log.debug("WOPI PUT: HTTP %s, lock=%s...", res.status_code, lock_id[:16])
    if res.status_code != 200:
        wopi_lock = res.headers.get("x-wopi-lock", "—")
        log.warning("WOPI PUT отклонён: status=%s, server_lock=%s", res.status_code, wopi_lock)
    return res


async def _try_put_with_lock(session: WopiSession, client: httpx.AsyncClient, data: bytes) -> bool:
    """
    Пробует зафиксировать файл сначала с текущей сессионной блокировкой, затем с новой.

    Реализует механизм восстановления (fallback): если старый lock_id истек,
    захватывает новый уникальный замок и после записи корректно освобождает его.

    Возвращает True в случае успешной фиксации данных, иначе False.
    """
    if session.lock_id:
        res = await put_wopi_contents(session, client, data, session.lock_id)
        if res.status_code == 200:
            return True
    new_lock = str(uuid.uuid4())
    if not await acquire_wopi_lock(session, client, new_lock):
        log.warning("Не удалось захватить новый WOPI lock")
        return False
    res = await put_wopi_contents(session, client, data, new_lock)
    await release_wopi_lock(session, client, new_lock)
    return res.status_code == 200


async def upload_workbook(session: WopiSession, wb: openpyxl.Workbook) -> bool:
    """
    Сохраняет книгу openpyxl и выгружает обновленную версию на Яндекс Диск по WOPI.

    Координирует сериализацию байтов, инжекцию кэша формул и безопасную отправку
    через протокол блокировок.

    Возвращает True при успешном сохранении таблицы, иначе False.
    """
    data = await asyncio.to_thread(save_workbook_to_bytes, wb)
    async with httpx.AsyncClient(timeout=30.0) as client:
        if await _try_put_with_lock(session, client, data):
            log.info("✅ Таблица успешно сохранена (%s байт)", len(data))
            return True
    log.error("❌ Ошибка загрузки таблицы в WOPI")
    return False


async def verify_upload(
    session: WopiSession,
    target_date: date,
    lesson_num: int,
    expected_marks: dict[str, str],
) -> bool:
    """
    Легковесно валидирует сохранение отметок путем прямого анализа XML листа.

    Скачивает бинарные байты без создания тяжелого объекта openpyxl,
    проверяя физическое присутствие символов на сервере.

    Возвращает True, если сохраненные отметки подтверждены, иначе False.
    """
    try:
        raw = await _download_raw_bytes(session)
        return _verify_marks_in_raw(raw, target_date, expected_marks)
    except Exception as e:
        log.warning("Верификация не удалась (%s): %s", type(e).__name__, e)
        return False


async def _download_raw_bytes(session: WopiSession) -> bytes:
    """
    Скачивает сырые байты файла таблицы с сервера WOPI для верификации.

    Используется для быстрой проверки целостности без накладных расходов на парсинг.

    Возвращает бинарные байты xlsx файла или выбрасывает RuntimeError.
    """
    url = f"{session.resource_url}/contents?access_token={session.access_token}"
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        res = await client.get(url)
        if res.status_code != 200:
            raise RuntimeError(f"Верификация: HTTP {res.status_code}")
        log.debug("Верификация: скачано %s байт", len(res.content))
        return res.content


def _find_sheet_rid(wb_xml: str, sheet_name: str) -> str | None:
    """
    Находит relationship ID (r:id) листа в структуре workbook.xml.

    Использует защищенный парсер defusedxml для извлечения идентификатора связи
    по имени вкладки месяца.

    Возвращает строковый ID связи вида 'rId1' или None при отсутствии листа.
    """
    try:
        root = ET.fromstring(wb_xml)
        for sheet in root.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet"):
            if sheet.attrib.get("name") == sheet_name:
                for key, val in sheet.attrib.items():
                    if key.endswith("id"):
                        return val
        return None
    except Exception as e:
        log.warning("Ошибка парсинга workbook.xml: %s", e)
        return None


def _resolve_sheet_target_path(rels_xml: str, rid: str) -> str | None:
    """
    Определяет путь к файлу XML листа внутри zip-пакета по его relationship ID.

    Нормализует путь цели из workbook.xml.rels с префиксом 'xl/'.

    Возвращает путь в zip-архиве (напр. 'xl/worksheets/sheet1.xml') или None.
    """
    try:
        root = ET.fromstring(rels_xml)
        for rel in root.iter():
            if rel.attrib.get("Id") == rid:
                target = rel.attrib.get("Target", "").lstrip("/")
                return target if target.startswith("xl/") else f"xl/{target}"
        return None
    except Exception as e:
        log.warning("Ошибка парсинга workbook.xml.rels: %s", e)
        return None


def _extract_sheet_xml(raw: bytes, sheet_name: str) -> str | None:
    """
    Извлекает строковое XML-содержимое листа по имени напрямую из zip-архива xlsx.

    Осуществляет быстрый доступ к целевому листу без создания структур книги в памяти.

    Возвращает декодированный XML-текст листа или None при ошибке распаковки.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            if "xl/workbook.xml" not in zf.namelist() or "xl/_rels/workbook.xml.rels" not in zf.namelist():
                return None
            wb_xml = zf.read("xl/workbook.xml").decode("utf-8")
            rid = _find_sheet_rid(wb_xml, sheet_name)
            if not rid:
                return None
            rels_xml = zf.read("xl/_rels/workbook.xml.rels").decode("utf-8")
            path = _resolve_sheet_target_path(rels_xml, rid)
            if path and path in zf.namelist():
                return zf.read(path).decode("utf-8")
        return None
    except Exception as e:
        log.warning("Сбой распаковки листа '%s': %s", sheet_name, e)
        return None


def _cell_has_expected_mark(cell_xml: str, mark: str) -> bool:
    """
    Проверяет соответствие отметки посещаемости в XML-фрагменте ячейки.

    Распознает символы в тегах <t> и <v>, корректно декодируя HTML-сущности.

    Возвращает True, если значение ячейки совпадает с ожидаемой отметкой, иначе False.
    """
    unescaped = html.unescape(cell_xml)
    match = re.search(r"<(?:\w+:)?(?:t|v)[^>]*>([^<]*)</(?:\w+:)?(?:t|v)>", unescaped)
    return bool(match and match.group(1).strip().upper() == mark)


def _marks_found_in_xml(xml_text: str, check_marks: dict[str, str]) -> bool:
    """
    Проверяет наличие ожидаемых отметок в сыром XML-тексте листа.

    Сканирует ячейки по номерам строк и сопоставляет значения с контрольной выборкой.

    Возвращает True, если все проверочные отметки обнаружены в XML.
    """
    found = 0
    for row_str, mark in check_marks.items():
        row_pat = rf'<c\s+r="[A-Z]+{row_str}"[^>]*>.*?</c>'
        for cell_match in re.finditer(row_pat, xml_text):
            if _cell_has_expected_mark(cell_match.group(0), mark):
                found += 1
                break
    ok = found == len(check_marks)
    if not ok:
        log.warning("Верификация: найдено %s/%s отметок", found, len(check_marks))
    else:
        log.info("Верификация: все %s отметок подтверждены ✓", found)
    return ok


def _verify_marks_in_raw(raw: bytes, target_date: date, expected_marks: dict[str, str]) -> bool:
    """
    Координирует низкоуровневую верификацию отметок в байтах книги.

    Определяет имя листа месяца, извлекает его XML и проверяет совпадение отметок.

    Возвращает True в случае успешного подтверждения, False при расхождениях.
    """
    sheet_name = MONTH_SHEET_MAP.get(target_date.month)
    if not sheet_name:
        return False
    check_marks = {r: m for r, m in expected_marks.items() if m in {"О", "У", "Н"}}
    if not check_marks:
        check_marks = dict(list(expected_marks.items())[:3])
    xml_text = _extract_sheet_xml(raw, sheet_name)
    if not xml_text:
        log.warning("Верификация: XML листа '%s' не найден", sheet_name)
        return False
    return _marks_found_in_xml(xml_text, check_marks)


def get_month_sheet(wb: openpyxl.Workbook, target_date: date) -> Worksheet:
    """
    Возвращает рабочий лист книги openpyxl, соответствующий месяцу даты.

    Сопоставляет номер месяца по календарному словарю MONTH_SHEET_MAP.

    Возвращает экземпляр Worksheet или выбрасывает ValueError.
    """
    sheet_name = MONTH_SHEET_MAP.get(target_date.month)
    if not sheet_name or sheet_name not in wb.sheetnames:
        raise ValueError(f"Вкладка '{sheet_name}' для месяца {target_date.month} не найдена")
    return wb[sheet_name]


def parse_date_cell(cell_value: object) -> str | None:
    """
    Приводит значение ячейки даты к стандартизированной строке 'ДД.ММ'.

    Поддерживает парсинг объектов datetime, date и строковых представлений.

    Возвращает строковую дату 'ДД.ММ' или None при пустом значении.
    """
    if isinstance(cell_value, (datetime, date)):
        return cell_value.strftime("%d.%m")
    if cell_value:
        return str(cell_value).strip()
    return None


def find_date_column_start(sheet: Worksheet, target_date: date) -> int | None:
    """
    Находит начальную колонку даты во второй строке таблицы посещаемости.

    Ищет подстроку 'ДД.ММ' в шапке календаря месяца для определения блока пар дня.

    Возвращает 1-based номер начальной колонки или None при отсутствии даты.
    """
    target_str = target_date.strftime("%d.%m")
    for col in range(1, sheet.max_column + 1):
        parsed = parse_date_cell(sheet.cell(2, col).value)
        if parsed and target_str in parsed:
            log.debug("Найдена дата %s в колонке %s", target_str, col)
            return col
    return None


def find_lesson_column(sheet: Worksheet, target_date: date, lesson_num: int) -> int | None:
    """
    Определяет точный номер колонки для конкретного номера учебной пары дня.

    Сначала находит начальную колонку дня, затем сканирует строку 4 в поисках
    соответствующего номера пары (1-6).

    Возвращает целочисленный 1-based индекс колонки или None.
    """
    start_col = find_date_column_start(sheet, target_date)
    if not start_col:
        return None
    for offset in range(6):
        col = start_col + offset
        pair_val = sheet.cell(4, col).value
        if pair_val == lesson_num or str(pair_val) == str(lesson_num):
            log.debug("Найдена пара %s в колонке %s", lesson_num, col)
            return col
    return None


def normalize_fio(name: str) -> str:
    """
    Очищает строковое ФИО от неразрывных пробелов и лишних краевых знаков.

    Обеспечивает консистентное сравнение имен при невидимых различиях в пробелах.

    Возвращает очищенную строку ФИО в едином формате.
    """
    return name.replace("\xa0", " ").strip()


def get_students_list(sheet: Worksheet) -> list[tuple[int, str]]:
    """
    Извлекает список студентов академической группы из колонки B таблицы.

    Считывает строки с 5 по max_row, очищая имена и исключая пустые ячейки.

    Возвращает список кортежей (номер_строки, нормализованное_ФИО).
    """
    students: list[tuple[int, str]] = []
    for row in range(5, sheet.max_row + 1):
        val = sheet.cell(row, 2).value
        if not val:
            continue
        cleaned = normalize_fio(str(val))
        if cleaned:
            students.append((row, cleaned))
    return students


def find_student_row(sheet: Worksheet, student_name: str) -> int | None:
    """
    Находит номер строки студента в таблице по имени или фамилии.

    Применяет нечувствительное к регистру частичное совпадение подстрок для надежности.

    Возвращает номер строки в таблице (5-36) или None, если студент не найден.
    """
    target = normalize_fio(student_name).lower()
    for row, name in get_students_list(sheet):
        if target in name.lower() or name.lower() in target:
            return row
    return None


def write_student_mark(
    sheet: Worksheet,
    row: int,
    col: int,
    mark: str,
) -> None:
    """
    Записывает валидированную отметку посещаемости в целевую ячейку листа.

    Проверяет принадлежность символа разрешенному алфавиту ('П', 'О', 'У', 'Н', '')
    и логирует координаты записи.

    Не возвращает значений; обновляет свойство value ячейки или выбрасывает ValueError.
    """
    valid_marks = {"П", "О", "У", "Н", ""}
    clean_mark = mark.strip().upper()
    if clean_mark not in valid_marks:
        raise ValueError(f"Недопустимая отметка посещаемости: {mark}")
    cell = sheet.cell(row, col)
    cell.value = clean_mark if clean_mark else None
    log.debug("Записана отметка '%s' в ячейку R%sC%s", clean_mark, row, col)
