FROM python:3.9
WORKDIR /app

RUN pip install pymysql
RUN pip install confluent_kafka
RUN pip install pytz
RUN pip install kafka-python

COPY alert_system/alert_system.py . 
COPY common/ ./common
COPY ./admin_kafka /app/admin_kafka

RUN pip install sqlalchemy psycopg2-binary confluent-kafka
ENV DATABASE_URL=postgresql://Matteo:123ciao@database:5432/MatteoDB
CMD ["python", "alert_system.py"]