# Dockerfile for the LMS Telegram Bot

FROM python:3.14

RUN pip install --no-cache-dir uv

WORKDIR /bot

COPY pyproject.toml .

RUN uv sync --no-dev

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["uv", "run", "bot.py"]