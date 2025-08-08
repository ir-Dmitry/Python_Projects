# FROM python:3.9-slim

# WORKDIR /app

# COPY . /app

# RUN pip install --no-cache-dir -r requirements.txt

# EXPOSE 8080

# CMD ["python", "main.py"]

# Этап сборки зависимостей
FROM python:3.9-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.9-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

# Удаляем tzdata, если он был установлен, чтобы сэкономить место
RUN apt-get purge -y tzdata && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Задаём переменную окружения для московского часового пояса
ENV TZ=Europe/Moscow

EXPOSE 8080

CMD ["python", "main.py"]

