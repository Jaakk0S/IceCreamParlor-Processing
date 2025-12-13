FROM python:3.9-alpine

RUN pip install pika pyyaml dotenv

COPY config.yaml ./
COPY process.py ./
COPY .env ./

ENTRYPOINT ["python", "process.py"]