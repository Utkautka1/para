"""
Управление асинхронным gRPC сервером para-api.

Запускает gRPC сервер на базе grpc.aio с пулом потоков и регистрацией
сервисеров расписания, экзаменов и преподавателей.
"""


import grpc

from api.grpc.servicers import ExamsServicer, ScheduleServicer, TeachersServicer
from api.proto import exams_pb2_grpc, schedule_pb2_grpc, teachers_pb2_grpc
from config import GRPC_MAX_MESSAGE_LENGTH
from core.logger import get_logger

log = get_logger("grpc_server")


def _register_servicers(server: grpc.aio.Server) -> None:
    """Регистрирует все gRPC сервисеры на сервере."""
    schedule_pb2_grpc.add_ScheduleServiceServicer_to_server(ScheduleServicer(), server)
    exams_pb2_grpc.add_ExamsServiceServicer_to_server(ExamsServicer(), server)
    teachers_pb2_grpc.add_TeachersServiceServicer_to_server(TeachersServicer(), server)


def create_grpc_server() -> grpc.aio.Server:
    """Создает и настраивает экземпляр gRPC сервера."""
    options = [
        ("grpc.max_receive_message_length", GRPC_MAX_MESSAGE_LENGTH),
        ("grpc.max_send_message_length", GRPC_MAX_MESSAGE_LENGTH),
    ]
    server = grpc.aio.server(options=options)
    _register_servicers(server)
    return server


async def start_grpc_server(server: grpc.aio.Server, host: str, port: int) -> None:
    """Привязывает сокет и запускает обработку gRPC соединений."""
    listen_addr = f"{host}:{port}"
    server.add_insecure_port(listen_addr)
    log.info(f"🚀 Запуск gRPC сервера на {listen_addr}")
    await server.start()


async def stop_grpc_server(server: grpc.aio.Server | None, grace: float = 5.0) -> None:
    """Останавливает gRPC сервер с ожиданием завершения активных вызовов."""
    if server is not None:
        log.info(f"🛑 Остановка gRPC сервера (grace={grace}s)...")
        await server.stop(grace=grace)
        log.info("✅ gRPC сервер успешно остановлен")
