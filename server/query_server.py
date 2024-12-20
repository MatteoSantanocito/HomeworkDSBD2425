import logging
import re
import grpc
import service_pb2
import service_pb2_grpc
from common.database import SessionLocal
from common import models

logger = logging.getLogger(__name__)

def is_valid_email(email):
    regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(regex, email) is not None

class UserQueryService(service_pb2_grpc.UserQueryServiceServicer):

    def GetLatestValue(self, request, context):
        if not request.email:
            context.set_details("Missing email.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.GetLatestValueResponse()

        if not is_valid_email(request.email):
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
            context.set_details("Non trovata nessuna email.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.GetAverageValueResponse()

        if not is_valid_email(request.email):
            logger.info(f"Formato email non valido: {request.email}")
            context.set_details("Email non valida.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.GetAverageValueResponse()

        if request.count <= 0:
            context.set_details("Deve essere positivo il numero.")
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