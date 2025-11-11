FROM python:3.9-alpine

ENV rabbitmq_username=admin
ENV rabbitmq_password=password

COPY config.yaml ./
COPY process.py ./

RUN ["python", "process.py"]