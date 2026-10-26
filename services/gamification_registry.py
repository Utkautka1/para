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

STAROSTA_RANK = RankDefinition(
    name="Староста группы (Вне рейтинга)",
    icon="👑",
    description="Отец-основатель и Староста 1-КПД-3. Действует вне общего академического рейтинга.",
    min_pct=100.0,
    max_pct=100.0,
    min_n=0,
    max_n=0,
)

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
        AchievementDefinition("att_ghost", "Учебный рывок", "Посетить более 30 учебных занятий за семестр", "⚡", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("att_critical_9", "Стабильный темп", "Преодолеть рубеж в 50 посещенных пар", "🎯", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("att_comeback", "Великий камбэк", "Выйти из зоны риска и закрыть долги справками", "🚀", c, AchievementRarity.RARE, 120),
        AchievementDefinition("att_doc_master", "Коллекционер справок", "Собрать более 3 пропусков по уважительной причине ('У')", "📋", c, AchievementRarity.COMMON, 60),
        AchievementDefinition("att_doc_legend", "Медицинский щит", "Накопить более 6 официальных справок", "🏥", c, AchievementRarity.RARE, 150),
    ]


def _get_punctuality_achievements() -> list[AchievementDefinition]:
    """Возвращает 10 достижений пунктуальности и тайминга."""
    c = AchievementCategory.PUNCTUALITY
    return [
        AchievementDefinition("late_first", "Первый звонок", "Получить первое в семестре опоздание на пару", "🔔", c, AchievementRarity.COMMON, 20),
        AchievementDefinition("late_serial", "В шаге от рекорда", "Посетить 10 и более занятий без единого опоздания", "🚦", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("late_zero", "Часы с кукушкой", "Ни одного опоздания за весь учебный процесс", "🕰️", c, AchievementRarity.RARE, 150),
        AchievementDefinition("time_early_bird", "Ранняя пташка", "Проверить расписание в боте до 08:00 утра", "🌅", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("time_night_owl", "Полуночник", "Посмотреть расписание на завтра после 21:00", "🦉", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("time_sunday_scout", "Воскресная разведка", "Изучить пары понедельника в выходной день", "🔍", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("time_second_shift", "Вторая смена", "Изучить пары со второй пары по расписанию", "☕", c, AchievementRarity.COMMON, 30),
        AchievementDefinition("time_bell_on", "Звонарь", "Включить автоматические напоминания о начале пар", "🔔", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("time_bell_silent", "Режим тишины", "Использовать тихий режим просмотра расписания", "🔕", c, AchievementRarity.COMMON, 30),
        AchievementDefinition("time_exact_arrival", "Идеальный тайминг", "Закрыть учебную неделю с 0 опозданий", "⏱️", c, AchievementRarity.RARE, 80),
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
        AchievementDefinition("bot_miniapp", "Новый горизонт", "Открыть Telegram Mini App интерфейс рейтинга", "📱", c, AchievementRarity.RARE, 150),
        AchievementDefinition("bot_manual", "Чтение инструкции", "Ознакомиться с возможностями через команду /help", "📖", c, AchievementRarity.COMMON, 20),
    ]


def _get_ai_achievements() -> list[AchievementDefinition]:
    """Возвращает 10 достижений работы с ИИ и домашними заданиями."""
    c = AchievementCategory.AI_HOMEWORK
    return [
        AchievementDefinition("ai_first_task", "Слава роботам", "Отправить первое задание в топик ДЗ для DeepSeek", "🤖", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("ai_gost_docx", "ГОСТ соблюден", "Сгенерировать готовый реферат в формате Word (.docx)", "📄", c, AchievementRarity.RARE, 100),
        AchievementDefinition("ai_prompt_pro", "Промпт-инженер", "Сформулировать подробный промпт с условиями задачи", "🧠", c, AchievementRarity.COMMON, 60),
        AchievementDefinition("ai_speedrun", "Сдал за 5 минут", "Решить домашнее задание в день его публикации", "⚡", c, AchievementRarity.RARE, 90),
        AchievementDefinition("ai_deepseek_fan", "Друг DeepSeek", "Решить более 3 академических заданий с помощью ИИ", "🌟", c, AchievementRarity.RARE, 150),
        AchievementDefinition("ai_title_page", "Титульник по ГОСТу", "Получить документ с выверенным титульным листом", "📑", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("ai_night_grind", "Ночной дедлайн", "Отправить задачу на решение в ночные часы (22:00–06:00)", "🌙", c, AchievementRarity.RARE, 80),
        AchievementDefinition("ai_polymath", "Энциклопедист", "Решить задания по нескольким учебным дисциплинам", "📚", c, AchievementRarity.EPIC, 200),
        AchievementDefinition("ai_clean_code", "Чистый код", "Сгенерировать лабораторную работу с рабочим скриптом", "💻", c, AchievementRarity.RARE, 120),
        AchievementDefinition("ai_hero", "Помощь товарищу", "Поделиться решением задачи с одногруппниками", "🦸", c, AchievementRarity.COMMON, 50),
    ]


def _get_student_life_achievements() -> list[AchievementDefinition]:
    """Возвращает 10 достижений студенческой жизни 1-КПД-3."""
    c = AchievementCategory.STUDENT_LIFE
    return [
        AchievementDefinition("life_mdk_pro", "Знаток МДК", "Посетить более 40 учебных занятий семестра", "🎯", c, AchievementRarity.RARE, 120),
        AchievementDefinition("life_sport_king", "Спортивная форма", "Удерживать общую посещаемость выше 90%", "🏃", c, AchievementRarity.RARE, 100),
        AchievementDefinition("life_zoom_click", "Клик в Zoom", "Подключиться к дистанционной паре по ссылке в боте", "🔗", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("life_exam_ready", "К сессии готов", "Изучить актуальное расписание зачетов и экзаменов", "🎓", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("life_faculty_guide", "Преподавательский состав", "Посмотреть контакты и кабинеты преподавателей", "👨‍🏫", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("life_window_chill", "Форточка", "Проверить расписание во время перерыва между парами", "🪟", c, AchievementRarity.COMMON, 30),
        AchievementDefinition("life_monday_win", "Тяжелый понедельник", "Начать учебную неделю без единого пропуска", "🌅", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("life_friday_party", "Пятничный финиш", "Закрыть учебную пятницу с отличной посещаемостью", "🎉", c, AchievementRarity.COMMON, 60),
        AchievementDefinition("life_math_god", "Академический стандарт", "Преодолеть планку в 60 посещенных занятий", "📐", c, AchievementRarity.RARE, 110),
        AchievementDefinition("life_future_senior", "Будущий Senior", "Посещаемость выше 85% и более 50 посещенных пар", "🖥️", c, AchievementRarity.RARE, 120),
    ]


def _get_social_achievements() -> list[AchievementDefinition]:
    """Возвращает 10 достижений социальной активности."""
    c = AchievementCategory.SOCIAL
    return [
        AchievementDefinition("soc_birthday", "Именинник", "Быть внесенным в календарь дней рождения группы", "🎂", c, AchievementRarity.RARE, 100),
        AchievementDefinition("soc_heart", "Душа компании", "Поздравить одногруппника с днем рождения в чате", "❤️", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("soc_headman_ally", "Связь со старостой", "Оперативно ответить на утреннюю перекличку", "🤝", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("soc_ping_muster", "Общий сбор", "Увидеть экстренный пинг группы и вовремя среагировать", "📢", c, AchievementRarity.COMMON, 30),
        AchievementDefinition("soc_veteran", "Костяк 1-КПД-3", "Активный студент группы с начала учебного года", "🏛️", c, AchievementRarity.RARE, 100),
        AchievementDefinition("soc_pulse_boost", "Пульс группы", "Личная посещаемость превышает средний пульс группы", "💓", c, AchievementRarity.RARE, 90),
        AchievementDefinition("soc_meme_lord", "Мемолог 1-КПД-3", "Использовать локальные стикеры и мемы группы", "🎭", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("soc_poll_citizen", "Гражданский долг", "Принять участие в голосовании или опросе группы", "🗳️", c, AchievementRarity.COMMON, 30),
        AchievementDefinition("soc_colloquium", "Коллоквиум", "Участвовать в совместном разборе сложных учебных тем", "💡", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("soc_solidarity", "Солидарность", "Поддержать товарищей перед зачетной сессией", "✊", c, AchievementRarity.COMMON, 50),
    ]


def _get_easter_egg_achievements() -> list[AchievementDefinition]:
    """Возвращает 10 юбилейных достижений и пасхалок."""
    c = AchievementCategory.EASTER_EGGS
    return [
        AchievementDefinition("egg_jubilee_300", "Юбиляр 300", "Участник академической системы Para 1-КПД-3", "🎖️", c, AchievementRarity.LEGENDARY, 500),
        AchievementDefinition("egg_konami", "Код Конами", "Обнаружить скрытую пасхалку в интерфейсе Mini App", "🎮", c, AchievementRarity.EPIC, 250),
        AchievementDefinition("egg_matrix", "Матрица КТМУ", "Включить ночную киберпанк тему в интерфейсе", "🕶️", c, AchievementRarity.RARE, 80),
        AchievementDefinition("egg_speed_click", "Быстрый клик", "Открыть расписание в один клик через инлайн-меню", "⚡", c, AchievementRarity.COMMON, 50),
        AchievementDefinition("egg_tapper", "Тапер года", "Совершить более 25 взаимодействий с ботом и MiniApp", "👆", c, AchievementRarity.RARE, 120),
        AchievementDefinition("egg_api_hacker", "Исследователь", "Изучить все вкладки и разделы Telegram Mini App", "💻", c, AchievementRarity.EPIC, 200),
        AchievementDefinition("egg_tracer", "Аналитик", "Регулярно запрашивать персональную статистику пар", "🛰️", c, AchievementRarity.EPIC, 200),
        AchievementDefinition("egg_cleaner", "Чистюля", "Закрыть временные диалоговые сообщения бота", "🧹", c, AchievementRarity.COMMON, 30),
        AchievementDefinition("egg_tea_break", "Большая перемена", "Просмотреть расписание в дневное время (11:00–14:00)", "☕", c, AchievementRarity.COMMON, 40),
        AchievementDefinition("egg_vip", "Почетный студент", "Посещаемость выше 95% или благодарность старостата", "💎", c, AchievementRarity.LEGENDARY, 400),
    ]


def _get_mastery_achievements() -> list[AchievementDefinition]:
    """Возвращает 10 высших достижений мастерства и статуса."""
    c = AchievementCategory.MASTERY
    return [
        AchievementDefinition("mast_first_course", "ОХ ПЕРВЫЙ КУРС! ПОНЯЛИ?!", "Достичь точно 80% посещаемости и получить легендарный мем-титул", "🎯", c, AchievementRarity.EPIC, 300),
        AchievementDefinition("mast_normis_life", "Нормис по жизни", "Успешно закрепиться в статусе Нормис группы (81–89%)", "☕", c, AchievementRarity.RARE, 100),
        AchievementDefinition("mast_favorite", "Фаворит деканата", "Достичь статуса 'Любимчик старосты' с идеальным журналом", "👑", c, AchievementRarity.LEGENDARY, 500),
        AchievementDefinition("mast_xp_1000", "Тысячник XP", "Накопить более 1 000 очков академического опыта", "✨", c, AchievementRarity.RARE, 150),
        AchievementDefinition("mast_xp_5000", "Опытный волк", "Преодолеть рубеж в 2 500 очков академического опыта", "🔥", c, AchievementRarity.EPIC, 350),
        AchievementDefinition("mast_all_rounder", "Универсал", "Открыть хотя бы по одной ачивке в 4 разных категориях", "🌈", c, AchievementRarity.EPIC, 300),
        AchievementDefinition("mast_badge_collector", "Коллекционер бейджей", "Разблокировать более 10 уникальных достижений", "🏅", c, AchievementRarity.EPIC, 250),
        AchievementDefinition("mast_top3", "Топ-3 группы", "Войти в тройку лидеров академического рейтинга 1-КПД-3", "🥉", c, AchievementRarity.EPIC, 300),
        AchievementDefinition("mast_top1", "Золотой пьедестал", "Занять 1-е место в группе по дисциплине и посещаемости", "🥇", c, AchievementRarity.LEGENDARY, 600),
        AchievementDefinition("mast_grandmaster", "Гроссмейстер 1-КПД-3", "Разблокировать более 15 уникальных достижений", "🌟", c, AchievementRarity.LEGENDARY, 1000),
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
