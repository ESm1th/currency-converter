FROM python:3.7-alpine

WORKDIR /app

COPY converter /app

ENTRYPOINT ["python", "server.py"]
