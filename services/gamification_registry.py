"""
Реестр рангов и 80 достижений академической системы 1-КПД-3.

Содержит:
  1. Шкалу рангов посещаемости с мемом "ОХ ПЕРВЫЙ КУРС! ПОНЯЛИ?!" на 80%
  2. Полный каталог из 80 уникальных достижений в 8 категориях
  3. Вспомогательные функции быстрого доступа к паспортам достижений
"""

from services.gamification_models import (
    AchievementCategory,
    AchievementDefinition,
    AchievementRarity,
    RankDefinition,
)

# ==============================================================================
# ШКАЛА АКАДЕМИЧЕСКИХ РАНГОВ
# ==============================================================================

RANKS: list[RankDefinition] = [
    RankDefinition(
        name="Любимчик старосты",
        icon="👑",
        description="Абсолютный чемпион группы: 100% пар, 0 пропусков и 0 опозданий.",
        min_pct=100.0,
        max_pct=100.0,
        min_n=0,
        max_n=0,
    ),
    RankDefinition(
        name="Легальный отличник",
        icon="🛡️",
        description="100% посещаемости: все пропуски прикрыты официальной справкой.",
        min_pct=100.0,
        max_pct=100.0,
        min_n=0,
        max_n=0,
    ),
    RankDefinition(
        name="Активист группы",
        icon="⭐",
        description="Почти идеальное посещение (95–99%), пара мелких опозданий.",
        min_pct=95.0,
        max_pct=99.9,
    ),
    RankDefinition(
        name="Стойкий студент",
        icon="🎖️",
        description="Отличная учебная дисциплина (90–94%), редкие пропуски.",
        min_pct=90.0,
        max_pct=94.9,
    ),
    RankDefinition(
        name="Нормис",
        icon="☕",
        description="Золотая середина (81–89%): ходит когда надо, не наглеет.",
        min_pct=81.0,
        max_pct=89.9,
    ),
    RankDefinition(
        name="ОХ ПЕРВЫЙ КУРС! ПОНЯЛИ?!",
        icon="🎯",
        description="Культовый мемный рубеж ровно в 80% посещаемости 1-КПД-3.",
        min_pct=79.5,
        max_pct=80.9,
    ),
    RankDefinition(
        name="Балансир",
        icon="⚠️",
        description="Ходит по лезвию ножа (70–79%), опасная близость к деканату.",
        min_pct=70.0,
        max_pct=79.4,
    ),
    RankDefinition(
        name="Злостный прогульщик",
        icon="🚨",
        description="Серия несанкционированных пропусков (55–69%), зона риска.",
        min_pct=55.0,
        max_pct=69.9,
    ),
    RankDefinition(
        name="Кандидат на отчисление",
        icon="⛔️",
        description="Критический уровень (35–54%), староста готовит приказ.",
        min_pct=35.0,
        max_pct=54.9,
    ),
    RankDefinition(
        name="Призрак КТМУ",
        icon="💀",
        description="Посещаемость ниже 35%. Легенда гласит, что он учится в 1-КПД-3.",
        min_pct=0.0,
        max_pct=34.9,
    ),
]


# ==============================================================================
# РЕЕСТР ИЗ 80 ДОСТИЖЕНИЙ
# ==============================================================================

def _get_attendance_achievements() -> list[AchievementDefinition]:
    """Возвращает 10 достижений категории посещаемости."""
    c = AchievementCategory.ATTENDANCE
    return [
        AchievementDefinition("att_100", "Клуб 100%", "Иметь 100% общую посещаемость пар", "🏆", c, AchievementRarity.EPIC, 250),
        AchievementDefinition("att_no_unexcused", "Без криминала", "Ни единого прогула без уважительной причины (0 'Н')", "🛡️", c, AchievementRarity.RARE, 150),
        AchievementDefinition("att_survivor_6", "Шесть кругов ада", "Пережить и посетить все 6 пар за один учебный день", "⚔️", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("att_full_week", "Железная неделя", "Полная учебная неделя без единого пропуска", "📅", c, AchievementRarity.RARE, 100),
        AchievementDefinition("att_month_streak", "Месяц дисциплины", "Закрыть календарный месяц с идеальным посещением", "🗓️", c, AchievementRarity.EPIC, 300),
        AchievementDefinition("att_ghost", "Человек-невидимка", "Накопить более 20 прогулов за всё время", "👻", c, AchievementRarity.COMMON, 30),
        AchievementDefinition("att_critical_9", "Хождение по краю", "Достичь ровно 9 прогулов — порог красной зоны", "🚨", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("att_comeback", "Великий камбэк", "Выйти из зоны риска и закрыть все долги", "🚀", c, AchievementRarity.RARE, 120),
        AchievementDefinition("att_doc_master", "Коллекционер справок", "Собрать более 5 пропусков по уважительной причине ('У')", "📋", c, AchievementRarity.COMMON, 60),
        AchievementDefinition("att_doc_legend", "Пожизненный больничный", "Накопить более 10 официальных справок", "🏥", c, AchievementRarity.RARE, 150),
    ]


def _get_punctuality_achievements() -> list[AchievementDefinition]:
    """Возвращает 10 достижений пунктуальности и тайминга."""
    c = AchievementCategory.PUNCTUALITY
    return [
        AchievementDefinition("late_first", "Первый звонок", "Получить первое в семестре опоздание на пару", "🔔", c, AchievementRarity.COMMON, 20),
        AchievementDefinition("late_serial", "Хронический затор", "Накопить 3 и более опозданий в журнале", "🚦", c, AchievementRarity.COMMON, 30),
        AchievementDefinition("late_zero", "Часы с кукушкой", "Ни одного опоздания за весь учебный процесс", "🕰️", c, AchievementRarity.RARE, 150),
        AchievementDefinition("time_early_bird", "Ранняя пташка", "Проверить расписание в боте до 07:00 утра", "🌅", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("time_night_owl", "Полуночник", "Посмотреть расписание на завтра после 23:00", "🦉", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("time_sunday_scout", "Воскресная разведка", "Изучить пары понедельника в воскресный вечер", "🔍", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("time_second_shift", "Вторая смена", "Прийти сразу ко второй паре по расписанию", "☕", c, AchievementRarity.COMMON, 30),
        AchievementDefinition("time_bell_on", "Звонарь", "Включить автоматические напоминания о начале пар", "🔔", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("time_bell_silent", "Режим тишины", "Использовать тихий режим напоминаний без звука", "🔕", c, AchievementRarity.COMMON, 30),
        AchievementDefinition("time_exact_arrival", "Секунда в секунду", "Зайти в аудиторию за минуту до звонка", "⏱️", c, AchievementRarity.RARE, 80),
    ]


def _get_bot_achievements() -> list[AchievementDefinition]:
    """Возвращает 10 достижений взаимодействия с ботом."""
    c = AchievementCategory.BOT_INTERACTION
    return [
        AchievementDefinition("bot_welcome", "Добро пожаловать в семью", "Первый запуск бота через команду /start", "👋", c, AchievementRarity.COMMON, 20),
        AchievementDefinition("bot_subscriber", "На связи", "Подписаться на ежедневную утреннюю рассылку", "📬", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("bot_f5_master", "F5 Мастер", "Принудительно обновить расписание кнопкой 'Обновить'", "🔄", c, AchievementRarity.COMMON, 30),
        AchievementDefinition("bot_future_peek", "Взгляд в будущее", "Посмотреть расписание на завтрашний день", "📆", c, AchievementRarity.COMMON, 30),
        AchievementDefinition("bot_week_next", "Стратег", "Изучить расписание на следующую неделю", "⏭️", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("bot_self_audit", "Самоконтроль", "Запросить личную статистику посещаемости /my_attendance", "📊", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("bot_voice_stt", "Голосовой адепт", "Отправить голосовое сообщение для нейро-транскрипции", "🎙️", c, AchievementRarity.RARE, 100),
        AchievementDefinition("bot_podcast", "Подкастер", "Расшифровать голосовое длительностью более 1 минуты", "🎧", c, AchievementRarity.RARE, 120),
        AchievementDefinition("bot_miniapp", "Новый горизонт", "Открыть Telegram Mini App интерфейс", "📱", c, AchievementRarity.RARE, 150),
        AchievementDefinition("bot_manual", "Чтение инструкции", "Ознакомиться с возможностями через команду /help", "📖", c, AchievementRarity.COMMON, 20),
    ]


def _get_ai_achievements() -> list[AchievementDefinition]:
    """Возвращает 10 достижений работы с ИИ и домашними заданиями."""
    c = AchievementCategory.AI_HOMEWORK
    return [
        AchievementDefinition("ai_first_task", "Слава роботам", "Отправить первое задание в топик ДЗ для DeepSeek", "🤖", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("ai_gost_docx", "ГОСТ соблюден", "Сгенерировать готовый реферат в формате Word (.docx)", "📄", c, AchievementRarity.RARE, 100),
        AchievementDefinition("ai_prompt_pro", "Промпт-инженер", "Сформулировать подробный промпт с условиями задачи", "🧠", c, AchievementRarity.COMMON, 60),
        AchievementDefinition("ai_speedrun", "Сдал за 5 минут", "Решить домашнее задание в день его сдачи", "⚡", c, AchievementRarity.RARE, 90),
        AchievementDefinition("ai_deepseek_fan", "Друг DeepSeek", "Решить более 3 академических заданий с помощью ИИ", "🌟", c, AchievementRarity.RARE, 150),
        AchievementDefinition("ai_title_page", "Титульник по ГОСТу", "Получить документ с идеально выверенным титульным листом", "📑", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("ai_night_grind", "Ночной дедлайн", "Отправить задачу на решение в ночные часы (00:00–06:00)", "🌙", c, AchievementRarity.RARE, 80),
        AchievementDefinition("ai_polymath", "Энциклопедист", "Решить задания по 3 разным учебным дисциплинам", "📚", c, AchievementRarity.EPIC, 200),
        AchievementDefinition("ai_clean_code", "Чистый код", "Сгенерировать лабораторную работу с рабочим скриптом", "💻", c, AchievementRarity.RARE, 120),
        AchievementDefinition("ai_hero", "Спаситель группы", "Поделиться сгенерированным решением с одногруппниками", "🦸", c, AchievementRarity.COMMON, 50),
    ]


def _get_student_life_achievements() -> list[AchievementDefinition]:
    """Возвращает 10 достижений студенческой жизни 1-КПД-3."""
    c = AchievementCategory.STUDENT_LIFE
    return [
        AchievementDefinition("life_mdk_pro", "Знаток МДК", "Посетить все профильные пары междисциплинарного курса", "🎯", c, AchievementRarity.RARE, 120),
        AchievementDefinition("life_sport_king", "Физкультурник года", "Не пропустить ни одного занятия по физической культуре", "🏃", c, AchievementRarity.RARE, 100),
        AchievementDefinition("life_zoom_click", "Клик в Zoom", "Воспользоваться кнопкой прямого подключения к онлайн-паре", "🔗", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("life_exam_ready", "К сессии готов", "Изучить актуальное расписание зачетов и экзаменов", "🎓", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("life_faculty_guide", "Преподавательский состав", "Посмотреть контакты и кабинеты преподавателей", "👨‍🏫", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("life_window_chill", "Форточка", "Успешно провести окно между парами в колледже", "🪟", c, AchievementRarity.COMMON, 30),
        AchievementDefinition("life_monday_win", "Тяжелый понедельник", "Пережить 1-ю пару понедельника без опозданий", "🌅", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("life_friday_party", "Пятничный финиш", "Досидеть до конца последней пары в пятницу", "🎉", c, AchievementRarity.COMMON, 60),
        AchievementDefinition("life_math_god", "Повелитель интегралов", "Безупречная посещаемость математических дисциплин", "📐", c, AchievementRarity.RARE, 110),
        AchievementDefinition("life_future_senior", "Будущий Senior", "Посетить все лабораторные работы по программированию", "🖥️", c, AchievementRarity.RARE, 120),
    ]


def _get_social_achievements() -> list[AchievementDefinition]:
    """Возвращает 10 достижений социальной активности."""
    c = AchievementCategory.SOCIAL
    return [
        AchievementDefinition("soc_birthday", "Именинник", "Получить праздничное поздравление от бота в группе", "🎂", c, AchievementRarity.RARE, 100),
        AchievementDefinition("soc_heart", "Душа компании", "Поздравить одногруппника с днем рождения в чате", "❤️", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("soc_headman_ally", "Правая рука старосты", "Оперативно ответить на утреннюю перекличку", "🤝", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("soc_ping_muster", "Общий сбор", "Увидеть экстренный пинг группы и вовремя среагировать", "📢", c, AchievementRarity.COMMON, 30),
        AchievementDefinition("soc_veteran", "Старожил беседы", "Состоять в группе 1-КПД-3 с момента ее создания", "🏛️", c, AchievementRarity.RARE, 100),
        AchievementDefinition("soc_pulse_boost", "Пульс группы", "Внести вклад в общий академический пульс выше 75%", "💓", c, AchievementRarity.RARE, 90),
        AchievementDefinition("soc_meme_lord", "Мемолог 1-КПД-3", "Использовать локальные стикеры и мемы в топиках", "🎭", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("soc_poll_citizen", "Гражданский долг", "Принять участие в голосовании или академическом опросе", "🗳️", c, AchievementRarity.COMMON, 30),
        AchievementDefinition("soc_colloquium", "Коллоквиум", "Участвовать в групповом разборе сложной учебной темы", "💡", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("soc_solidarity", "Солидарность", "Поддержать товарища при сдаче практических работ", "✊", c, AchievementRarity.COMMON, 50),
    ]


def _get_easter_egg_achievements() -> list[AchievementDefinition]:
    """Возвращает 10 юбилейных достижений и пасхалок."""
    c = AchievementCategory.EASTER_EGGS
    return [
        AchievementDefinition("egg_jubilee_300", "Юбиляр 300", "Быть частью 1-КПД-3 в момент 300-го коммита Para!", "🎖️", c, AchievementRarity.LEGENDARY, 500),
        AchievementDefinition("egg_konami", "Код Конами", "Обнаружить скрытую пасхалку в интерфейсе Mini App", "🎮", c, AchievementRarity.EPIC, 250),
        AchievementDefinition("egg_matrix", "Матрица КТМУ", "Включить ночную киберпанк тему в Telegram", "🕶️", c, AchievementRarity.RARE, 80),
        AchievementDefinition("egg_speed_click", "Суперспринт", "Открыть расписание быстрее чем за 0.2 секунды", "⚡", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("egg_tapper", "Тапер года", "Совершить более 100 взаимодействий с кнопками бота", "👆", c, AchievementRarity.RARE, 120),
        AchievementDefinition("egg_api_hacker", "Хакер", "Успешно заглянуть в Swagger UI документацию API", "💻", c, AchievementRarity.EPIC, 200),
        AchievementDefinition("egg_tracer", "Трейсер", "Изучить спаны своих запросов в дашборде Jaeger", "🛰️", c, AchievementRarity.EPIC, 200),
        AchievementDefinition("egg_cleaner", "Чистюля", "Аккуратно закрыть все временные диалоговые меню бота", "🧹", c, AchievementRarity.COMMON, 30),
        AchievementDefinition("egg_tea_break", "Перерыв на чай", "Открыть бот ровно в 12:00 во время большой перемены", "☕", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("egg_vip", "VIP Персона", "Получить персональный статус или благодарность старосты", "💎", c, AchievementRarity.LEGENDARY, 400),
    ]


def _get_mastery_achievements() -> list[AchievementDefinition]:
    """Возвращает 10 высших достижений мастерства и статуса."""
    c = AchievementCategory.MASTERY
    return [
        AchievementDefinition("mast_first_course", "ОХ ПЕРВЫЙ КУРС! ПОНЯЛИ?!", "Достичь точно 80% посещаемости и получить легендарный мем-титул", "🎯", c, AchievementRarity.EPIC, 300),
        AchievementDefinition("mast_normis_life", "Нормис по жизни", "Успешно закрепиться в статусе Нормис группы", "☕", c, AchievementRarity.RARE, 100),
        AchievementDefinition("mast_favorite", "Фаворит деканата", "Достичь статуса 'Любимчик старосты' с идеальным журналом", "👑", c, AchievementRarity.LEGENDARY, 500),
        AchievementDefinition("mast_xp_1000", "Тысячник XP", "Накопить более 1 000 очков академического опыта", "✨", c, AchievementRarity.RARE, 150),
        AchievementDefinition("mast_xp_5000", "Опытный волк", "Преодолеть рубеж в 5 000 очков академического опыта", "🔥", c, AchievementRarity.EPIC, 350),
        AchievementDefinition("mast_all_rounder", "Универсал", "Открыть хотя бы по одной ачивке во всех 8 категориях", "🌈", c, AchievementRarity.EPIC, 300),
        AchievementDefinition("mast_badge_collector", "Коллекционер бейджей", "Разблокировать более 25 уникальных достижений", "🏅", c, AchievementRarity.EPIC, 250),
        AchievementDefinition("mast_top3", "Топ-3 группы", "Войти в тройку лидеров академического рейтинга 1-КПД-3", "🥉", c, AchievementRarity.EPIC, 300),
        AchievementDefinition("mast_top1", "Золотой пьедестал", "Занять 1-е место в группе по дисциплине и посещаемости", "🥇", c, AchievementRarity.LEGENDARY, 600),
        AchievementDefinition("mast_grandmaster", "Гроссмейстер 1-КПД-3", "Разблокировать 40+ достижений и стать абсолютной легендой", "🌟", c, AchievementRarity.LEGENDARY, 1000),
    ]


def get_all_achievements() -> list[AchievementDefinition]:
    """
    Формирует и возвращает полный реестр из ровно 80 достижений системы.

    Объединяет все 8 категорий по 10 достижений в каждой.
    """
    return (
        _get_attendance_achievements()
        + _get_punctuality_achievements()
        + _get_bot_achievements()
        + _get_ai_achievements()
        + _get_student_life_achievements()
        + _get_social_achievements()
        + _get_easter_egg_achievements()
        + _get_mastery_achievements()
    )


ACHIEVEMENTS_MAP: dict[str, AchievementDefinition] = {
    ach.id: ach for ach in get_all_achievements()
}
