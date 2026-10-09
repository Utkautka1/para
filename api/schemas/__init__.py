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
    TeachersRefreshResponse,
    TeachersResponse,
    TeacherSingleResponse,
)

__all__ = [
    "DayScheduleResponse",
    "WeekScheduleResponse",
    "CurrentLessonResponse",
    "ScheduleRefreshResponse",
    "ExamsResponse",
    "UpcomingExamsResponse",
    "ExamsRefreshResponse",
    "TeachersResponse",
    "TeacherSingleResponse",
    "TeacherSearchResponse",
    "CustomTeacherCreateRequest",
    "TeachersRefreshResponse",
    "AttendanceStatsResponse",
    "StudentPersonalStatsResponse",
    "ActiveSessionResponse",
    "StartSessionRequest",
    "MarkStudentRequest",
    "CommitAttendanceResponse",
    "ClassmatesListResponse",
    "ClassmateDetailResponse",
    "BirthdaysCalendarResponse",
    "UpcomingBirthdaysResponse",
    "TodayBirthdaysResponse",
    "SolverQueueStatusResponse",
    "DirectSolveRequest",
    "DirectSolveResponse",
    "TaskStatusResponse",
    "ClearQueueResponse",
    "SubscribersListResponse",
    "SubscriberCountResponse",
    "SubscriberStatusResponse",
    "SubscriberActionResponse",
    "SystemInfoResponse",
    "CacheFlushRequest",
    "CacheFlushResponse",
    "MiniappAuthRequest",
    "MiniappAuthResponse",
    "MiniappCheckResponse",
    "TesterListResponse",
    "TesterItemResponse",
]
