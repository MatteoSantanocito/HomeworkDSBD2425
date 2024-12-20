FROM python:3.9

WORKDIR /app

RUN pip install pymysql
RUN pip install bcrypt pymysql
RUN pip install cryptography
RUN pip install confluent_kafka
RUN pip install kafka-python
RUN pip install pytz

COPY common/ common/

COPY alert_notifier/requirements.txt .
COPY alert_notifier/notifier_template.py .
COPY alert_notifier/alert_notifier.py .
COPY ./admin_kafka /app/admin_kafka

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "alert_notifier.py"]