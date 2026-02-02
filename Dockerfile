FROM ubuntu:latest
FROM python:3.11-slim
LABEL authors="Mmadreza"

ENV PYTHONDONTWRITEMYCODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \ build-essential \ libpq-dev \ netcat-openbsd \ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]