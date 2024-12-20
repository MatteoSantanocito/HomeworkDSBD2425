import threading
import logging
from cachetools import TTLCache
import grpc
import service_pb2
import service_pb2_grpc

from class_operation import RegisterUserCommand, UpdateUserCommand, DeleteUserCommand, LoginUserCommand

logger = logging.getLogger(__name__)

class UserCommandService(service_pb2_grpc.UserCommandServiceServicer):
    def __init__(self):
        self.request_cache = TTLCache(maxsize=10000, ttl=600)
        self.operation_cache = TTLCache(maxsize=10000, ttl=300)
        self.cache_lock = threading.Lock()

    def RegisterUser(self, request, context):
        if not request.request_id:
            context.set_details("Non c'è il request_id")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.RegisterUserResponse(message="Request_id mancante.")

        with self.cache_lock:
            if request.request_id in self.request_cache:
                message = self.request_cache[request.request_id]
                logger.info(f"Rilevato request_id duplicato: {request.request_id}")
                return service_pb2.RegisterUserResponse(message=message)

        cmd = RegisterUserCommand(
            email=request.email,
            ticker=request.ticker,
            request_id=request.request_id,
            high_value=request.high_value,
            low_value=request.low_value
        )
        message, success, details, code = cmd.execute()

        with self.cache_lock:
            self.request_cache[request.request_id] = message

        if details:
            context.set_details(details)
        if code == "INTERNAL":
            context.set_code(grpc.StatusCode.INTERNAL)
        elif code == "NOT_FOUND":
            context.set_code(grpc.StatusCode.NOT_FOUND)

        return service_pb2.RegisterUserResponse(message=message)

    def UpdateUser(self, request, context):
        if not request.request_id:
            context.set_details("Nessun request_id.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.UpdateUserResponse(message="Request_id mancante")

        with self.cache_lock:
            if request.request_id in self.request_cache:
                message = self.request_cache[request.request_id]
                logger.info(f"Rilevato request_id duplicato: {request.request_id}")
                return service_pb2.UpdateUserResponse(message=message)

        cmd = UpdateUserCommand(
            email=request.email,
            ticker=request.ticker,
            request_id=request.request_id,
            high_value=request.high_value,
            low_value=request.low_value
        )
        message, success, details, code = cmd.execute()

        with self.cache_lock:
            self.request_cache[request.request_id] = message

        if details:
            context.set_details(details)
        if code == "INTERNAL":
            context.set_code(grpc.StatusCode.INTERNAL)
        elif code == "NOT_FOUND":
            context.set_code(grpc.StatusCode.NOT_FOUND)

        return service_pb2.UpdateUserResponse(message=message)

    def DeleteUser(self, request, context):
        if not request.request_id:
            context.set_details("Non è presente il request_id.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.DeleteUserResponse(message="Request_id mancante.")

        with self.cache_lock:
            if request.request_id in self.request_cache:
                message = self.request_cache[request.request_id]
                logger.info(f"Rilevato request_id duplicato: {request.request_id}")
                return service_pb2.DeleteUserResponse(message=message)

        cmd = DeleteUserCommand(
            email=request.email,
            request_id=request.request_id
        )
        message, success, details, code = cmd.execute()

        with self.cache_lock:
            self.request_cache[request.request_id] = message

        if details:
            context.set_details(details)
        if code == "INTERNAL":
            context.set_code(grpc.StatusCode.INTERNAL)
        elif code == "NOT_FOUND":
            context.set_code(grpc.StatusCode.NOT_FOUND)

        return service_pb2.DeleteUserResponse(message=message)

    def LoginUser(self, request, context):
        if not request.request_id:
            context.set_details("Manca la request_id.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.LoginUserResponse(message="Nessuna request_id.", success=False)

        with self.cache_lock:
            if request.request_id in self.request_cache:
                message = self.request_cache[request.request_id]
                success = True if message == "Login effettuato con successo." else False
                logger.info(f"Rilevato request_id duplicato: {request.request_id}")
                return service_pb2.LoginUserResponse(message=message, success=success)

        operation_key = f"LoginUser:{request.email}"
        with self.cache_lock:
            if operation_key in self.operation_cache:
                message, success = self.operation_cache[operation_key]
                self.request_cache[request.request_id] = message
                return service_pb2.LoginUserResponse(message=message, success=success)

        cmd = LoginUserCommand(email=request.email, request_id=request.request_id)
        message, success, details, code = cmd.execute()

        with self.cache_lock:
            self.request_cache[request.request_id] = message
            self.operation_cache[operation_key] = (message, success)

        if details:
            context.set_details(details)
        if code == "INTERNAL":
            context.set_code(grpc.StatusCode.INTERNAL)
        elif code == "NOT_FOUND":
            context.set_code(grpc.StatusCode.NOT_FOUND)

        return service_pb2.LoginUserResponse(message=message, success=success)