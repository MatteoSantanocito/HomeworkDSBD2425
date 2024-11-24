FROM python:3.9-slim

WORKDIR /app

COPY data_cleaner/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY data_cleaner/ .

COPY common/ ./common

ENV PYTHONUNBUFFERED=1

ENV DATABASE_URL=postgresql://Matteo:123ciao@database:5432/MatteoDB

CMD ["python", "cleaner.py"]