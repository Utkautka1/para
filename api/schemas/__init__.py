"""
Пакет Pydantic-схем para-api.
"""

from api.schemas.attendance import (
    ActiveSessionResponse,
    AttendanceStatsResponse,
    CommitAttendanceResponse,
    MarkStudentRequest,
    StartSessionRequest,
    StudentPersonalStatsResponse,
)
from api.schemas.birthdays import (
    BirthdaysCalendarResponse,
    TodayBirthdaysResponse,
    UpcomingBirthdaysResponse,
)
from api.schemas.classmates import (
    ClassmateDetailResponse,
    ClassmatesListResponse,
)
from api.schemas.exams import (
    ExamsRefreshResponse,
    ExamsResponse,
    UpcomingExamsResponse,
)
from api.schemas.miniapp import (
    MiniappAuthRequest,
    MiniappAuthResponse,
    MiniappCheckResponse,
    TesterItemResponse,
    TesterListResponse,
)
from api.schemas.schedule import (
    CurrentLessonResponse,
    DayScheduleResponse,
    ScheduleRefreshResponse,
    WeekScheduleResponse,
)
from api.schemas.solver import (
    ClearQueueResponse,
    DirectSolveRequest,
    DirectSolveResponse,
    SolverQueueStatusResponse,
    TaskStatusResponse,
)
from api.schemas.subscribers import (
    SubscriberActionResponse,
    SubscriberCountResponse,
    SubscribersListResponse,
    SubscriberStatusResponse,
)
from api.schemas.system import (
    CacheFlushRequest,
    CacheFlushResponse,
    SystemInfoResponse,
)
from api.schemas.teachers import (
    CustomTeacherCreateRequest,
    TeacherSearchResponse,
    TeacherSingleResponse,
    TeachersRefreshResponse,
    TeachersResponse,
)

__all__ = [
    "ActiveSessionResponse",
    "AttendanceStatsResponse",
    "BirthdaysCalendarResponse",
    "CacheFlushRequest",
    "CacheFlushResponse",
    "ClassmateDetailResponse",
    "ClassmatesListResponse",
    "ClearQueueResponse",
    "CommitAttendanceResponse",
    "CurrentLessonResponse",
    "CustomTeacherCreateRequest",
    "DayScheduleResponse",
    "DirectSolveRequest",
    "DirectSolveResponse",
    "ExamsRefreshResponse",
    "ExamsResponse",
    "MarkStudentRequest",
    "MiniappAuthRequest",
    "MiniappAuthResponse",
    "MiniappCheckResponse",
    "ScheduleRefreshResponse",
    "SolverQueueStatusResponse",
    "StartSessionRequest",
    "StudentPersonalStatsResponse",
    "SubscriberActionResponse",
    "SubscriberCountResponse",
    "SubscriberStatusResponse",
    "SubscribersListResponse",
    "SystemInfoResponse",
    "TaskStatusResponse",
    "TeacherSearchResponse",
    "TeacherSingleResponse",
    "TeachersRefreshResponse",
    "TeachersResponse",
    "TesterItemResponse",
    "TesterListResponse",
    "TodayBirthdaysResponse",
    "UpcomingBirthdaysResponse",
    "UpcomingExamsResponse",
    "WeekScheduleResponse",
]
