from concurrent import futures
import grpc
import time
import logging
from common.database import engine
from common import models
import service_pb2_grpc
from command_server import UserCommandService
from query_server import UserQueryService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_UserCommandServiceServicer_to_server(UserCommandService(), server)
    service_pb2_grpc.add_UserQueryServiceServicer_to_server(UserQueryService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("Server gRPC in esecuzione sulla porta 50051...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
        logger.info("Server gRPC stoppato.")

if __name__ == '__main__':
    serve()