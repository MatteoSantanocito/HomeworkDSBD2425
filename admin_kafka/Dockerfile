FROM python:3.9  

WORKDIR /app

RUN pip install confluent_kafka
RUN pip install kafka-python
RUN pip install pytz

COPY cluster_metadata.py .
COPY topic_creation.py .


CMD [ "python", "cluster_metadata.py"]