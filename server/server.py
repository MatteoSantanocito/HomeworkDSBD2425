from concurrent import futures
import grpc
import time
import re
import threading
from cachetools import TTLCache
import service_pb2
import service_pb2_grpc
from common.database import SessionLocal, engine
from common import models
import logging
from sqlalchemy.exc import OperationalError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

class UserServiceServicer(service_pb2_grpc.UserServiceServicer):
    def __init__(self):
        self.request_cache = TTLCache(maxsize=10000, ttl=600)
        self.operation_cache = TTLCache(maxsize=10000, ttl=300)
        self.cache_lock = threading.Lock()

    def is_valid_email(self, email):
        regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(regex, email) is not None

    def RegisterUser(self, request, context):
        if not request.request_id:
            context.set_details("Missing request_id.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.RegisterUserResponse(message="Missing request_id.")

        with self.cache_lock:
            if request.request_id in self.request_cache:
                message = self.request_cache[request.request_id]
                logger.info(f"Rilevato request_id duplicato: {request.request_id}")
                return service_pb2.RegisterUserResponse(message=message)

        if not self.is_valid_email(request.email):
            logger.info(f"Formato email non valido: {request.email}")
            message = "Email non valida."
            with self.cache_lock:
                self.request_cache[request.request_id] = message
            return service_pb2.RegisterUserResponse(message=message)

        if not request.ticker:
            logger.info("Ticker non può essere vuoto.")
            message = "Ticker non può essere vuoto."
            with self.cache_lock:
                self.request_cache[request.request_id] = message
            return service_pb2.RegisterUserResponse(message=message)

        session = SessionLocal()
        try:
            user = session.query(models.User).filter_by(email=request.email).first()
            if user:
                message = "Utente già registrato."
                logger.info(f"Utente già registrato: {request.email}")
            else:
                new_user = models.User(email=request.email, ticker=request.ticker)
                session.add(new_user)
                session.commit()
                message = "Registrazione effettuata con successo."
                logger.info(f"Nuovo utente registrato: {request.email}")

            with self.cache_lock:
                self.request_cache[request.request_id] = message

            return service_pb2.RegisterUserResponse(message=message)
        except Exception as e:
            logger.error(f"Errore in RegisterUser: {e}")
            context.set_details(f'Errore: {str(e)}')
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.RegisterUserResponse(message="Errore interno.")
        finally:
            session.close()

    def UpdateUser(self, request, context):
        if not request.request_id:
            context.set_details("Missing request_id.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.UpdateUserResponse(message="Missing request_id.")

        with self.cache_lock:
            if request.request_id in self.request_cache:
                message = self.request_cache[request.request_id]
                logger.info(f"Rilevato request_id duplicato: {request.request_id}")
                return service_pb2.UpdateUserResponse(message=message)

        if not self.is_valid_email(request.email):
            logger.info(f"Formato email non valido: {request.email}")
            message = "Email non valida."
            with self.cache_lock:
                self.request_cache[request.request_id] = message
            return service_pb2.UpdateUserResponse(message=message)

        if not request.ticker:
            logger.info("Ticker non può essere vuoto.")
            message = "Ticker non può essere vuoto."
            with self.cache_lock:
                self.request_cache[request.request_id] = message
            return service_pb2.UpdateUserResponse(message=message)

        session = SessionLocal()
        try:
            user = session.query(models.User).filter_by(email=request.email).first()
            if user:
                user.ticker = request.ticker
                session.commit()
                message = "Ticker aggiornato con successo."
                logger.info(f"Ticker aggiornato per: {request.email}")
            else:
                message = "Utente non trovato."
                logger.info(f"Utente non trovato: {request.email}")

            with self.cache_lock:
                self.request_cache[request.request_id] = message

            return service_pb2.UpdateUserResponse(message=message)
        except Exception as e:
            logger.error(f"Errore in UpdateUser: {e}")
            context.set_details(f'Errore: {str(e)}')
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.UpdateUserResponse(message="Errore interno.")
        finally:
            session.close()

    def DeleteUser(self, request, context):
        if not request.request_id:
            context.set_details("Missing request_id.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.DeleteUserResponse(message="Missing request_id.")

        with self.cache_lock:
            if request.request_id in self.request_cache:
                message = self.request_cache[request.request_id]
                logger.info(f"Rilevato request_id duplicato: {request.request_id}")
                return service_pb2.DeleteUserResponse(message=message)

        if not self.is_valid_email(request.email):
            logger.info(f"Formato email non valido: {request.email}")
            message = "Email non valida."
            with self.cache_lock:
                self.request_cache[request.request_id] = message
            return service_pb2.DeleteUserResponse(message=message)

        session = SessionLocal()
        try:
            user = session.query(models.User).filter_by(email=request.email).first()
            if user:
                session.delete(user)
                session.commit()
                message = "Account cancellato con successo."
                logger.info(f"Account cancellato per: {request.email}")
            else:
                message = "Utente non trovato."
                logger.info(f"Utente non trovato: {request.email}")

            with self.cache_lock:
                self.request_cache[request.request_id] = message

            return service_pb2.DeleteUserResponse(message=message)
        except Exception as e:
            logger.error(f"Errore in DeleteUser: {e}")
            context.set_details(f'Errore: {str(e)}')
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.DeleteUserResponse(message="Errore interno.")
        finally:
            session.close()

    def LoginUser(self, request, context):
        if not request.request_id:
            context.set_details("Missing request_id.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.LoginUserResponse(message="Missing request_id.", success=False)

        with self.cache_lock:
            if request.request_id in self.request_cache:
                message = self.request_cache[request.request_id]
                success = True if message == "Login effettuato con successo." else False
                logger.info(f"Rilevato request_id duplicato: {request.request_id}")
                return service_pb2.LoginUserResponse(message=message, success=success)

        if not self.is_valid_email(request.email):
            logger.info(f"Formato email non valido: {request.email}")
            message = "Email non valida."
            success = False
            with self.cache_lock:
                self.request_cache[request.request_id] = message
                self.operation_cache[f"LoginUser:{request.email}"] = (message, success)
            return service_pb2.LoginUserResponse(message=message, success=success)

        operation_key = f"LoginUser:{request.email}"
        with self.cache_lock:
            if operation_key in self.operation_cache:
                message, success = self.operation_cache[operation_key]
                self.request_cache[request.request_id] = message
                return service_pb2.LoginUserResponse(message=message, success=success)

        session = SessionLocal()
        try:
            user = session.query(models.User).filter_by(email=request.email).first()
            if user:
                message = "Login effettuato con successo."
                success = True
                logger.info(f"Utente loggato: {request.email}")
            else:
                message = "Utente non trovato."
                success = False
                logger.info(f"Utente non trovato: {request.email}")

            with self.cache_lock:
                self.request_cache[request.request_id] = message
                self.operation_cache[operation_key] = (message, success)

            return service_pb2.LoginUserResponse(message=message, success=success)
        except Exception as e:
            logger.error(f"Errore in LoginUser: {e}")
            context.set_details(f'Errore: {str(e)}')
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.LoginUserResponse(message="Errore interno.", success=False)
        finally:
            session.close()

    def GetLatestValue(self, request, context):
        if not request.email:
            context.set_details("Missing email.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.GetLatestValueResponse()

        if not self.is_valid_email(request.email):
            logger.info(f"Formato email non valido: {request.email}")
            context.set_details("Email non valida.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.GetLatestValueResponse()

        session = SessionLocal()
        try:
            user = session.query(models.User).filter_by(email=request.email).first()
            if not user:
                context.set_details("Utente non trovato.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return service_pb2.GetLatestValueResponse()

            ticker = user.ticker
            if not ticker:
                context.set_details("Ticker non impostato per l'utente.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return service_pb2.GetLatestValueResponse()

            latest_value = session.query(models.FinancialData).filter_by(ticker=ticker).order_by(models.FinancialData.timestamp.desc()).first()
            if latest_value:
                return service_pb2.GetLatestValueResponse(
                    email=request.email,
                    ticker=latest_value.ticker,
                    value=latest_value.value,
                    timestamp=latest_value.timestamp.isoformat()
                )
            else:
                context.set_details("Nessun valore disponibile per il ticker dell'utente.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return service_pb2.GetLatestValueResponse()
        except Exception as e:
            logger.error(f"Errore in GetLatestValue: {e}")
            context.set_details(f'Errore: {str(e)}')
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.GetLatestValueResponse()
        finally:
            session.close()

    def GetAverageValue(self, request, context):
        if not request.email:
            context.set_details("Missing email.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.GetAverageValueResponse()

        if not self.is_valid_email(request.email):
            logger.info(f"Formato email non valido: {request.email}")
            context.set_details("Email non valida.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.GetAverageValueResponse()

        if request.count <= 0:
            context.set_details("Count must be positive.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.GetAverageValueResponse()

        session = SessionLocal()
        try:
            user = session.query(models.User).filter_by(email=request.email).first()
            if not user:
                context.set_details("Utente non trovato.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return service_pb2.GetAverageValueResponse()

            ticker = user.ticker
            if not ticker:
                context.set_details("Ticker non impostato per l'utente.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return service_pb2.GetAverageValueResponse()

            values = session.query(models.FinancialData).filter_by(ticker=ticker).order_by(models.FinancialData.timestamp.desc()).limit(request.count).all()
            if values:
                average = sum(v.value for v in values) / len(values)
                return service_pb2.GetAverageValueResponse(
                    email=request.email,
                    ticker=ticker,
                    average_value=average
                )
            else:
                context.set_details("Nessun valore disponibile per il ticker dell'utente.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return service_pb2.GetAverageValueResponse()
        except Exception as e:
            logger.error(f"Errore in GetAverageValue: {e}")
            context.set_details(f'Errore: {str(e)}')
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.GetAverageValueResponse()
        finally:
            session.close()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("Server gRPC in esecuzione sulla porta 50051...")
    try:
        while True:
            time.sleep(86400)  
    except KeyboardInterrupt:
        server.stop(0)
        logger.info("Server gRPC fermato.")

if __name__ == '__main__':
    serve()