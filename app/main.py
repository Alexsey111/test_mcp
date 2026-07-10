from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
import pytz
import requests
import os
import time

app = FastAPI(title="Time Server API")

LOKI_URL = os.environ.get("LOKI_URL", "http://80.78.246.176:3100/loki/api/v1/push")
APP_NAME = os.environ.get("APP_NAME", "time-server")


def send_log_to_loki(message: str, level: str = "INFO", extra_labels: dict = None):
    """Отправляет лог напрямую в Loki через HTTP push API."""
    labels = {"app": APP_NAME, "level": level}
    if extra_labels:
        labels.update(extra_labels)

    timestamp_ns = str(int(time.time() * 1_000_000_000))

    payload = {
        "streams": [
            {
                "stream": labels,
                "values": [[timestamp_ns, message]],
            }
        ]
    }

    try:
        response = requests.post(LOKI_URL, json=payload, timeout=3)
        response.raise_for_status()
    except Exception as e:
        print(f"[LOKI ERROR] {e}")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    send_log_to_loki(
        f"{request.method} {request.url.path}",
        level="INFO",
        extra_labels={"endpoint": request.url.path},
    )
    return await call_next(request)


@app.get("/")
def root():
    send_log_to_loki("Запрос к корневому эндпоинту", level="INFO")
    return {"message": "Добро пожаловать в Time Server API"}


@app.get("/time")
def get_time():
    send_log_to_loki("Запрос текущего времени", level="INFO")
    return {"time": datetime.now(pytz.UTC).isoformat()}


@app.get("/date")
def get_date():
    send_log_to_loki("Запрос текущей даты", level="INFO")
    return {"date": datetime.now(pytz.UTC).date().isoformat()}


@app.get("/datetime")
def get_datetime():
    send_log_to_loki("Запрос текущей даты и времени", level="INFO")
    return {"datetime": datetime.now(pytz.UTC).isoformat()}


class ConvertRequest(BaseModel):
    time: str
    city: str


@app.post("/convert")
def convert_time(request: ConvertRequest):
    try:
        target_tz = pytz.timezone(request.city)
    except pytz.exceptions.UnknownTimeZoneError:
        send_log_to_loki(
            f"Неизвестный часовой пояс: {request.city}",
            level="ERROR",
            extra_labels={"endpoint": "/convert"},
        )
        raise HTTPException(
            status_code=400,
            detail=f"Неизвестный часовой пояс: {request.city}. Пример: Europe/Moscow",
        )

    try:
        dt = datetime.fromisoformat(request.time)
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
    except ValueError:
        send_log_to_loki(
            "Неверный формат времени в /convert",
            level="ERROR",
            extra_labels={"endpoint": "/convert"},
        )
        raise HTTPException(
            status_code=400,
            detail="Неверный формат времени. Используйте ISO 8601, например 2026-07-10T12:00:00",
        )

    converted = dt.astimezone(target_tz)
    send_log_to_loki(
        f"Конвертация времени: {request.time} -> {request.city}",
        level="INFO",
        extra_labels={"endpoint": "/convert"},
    )
    return {
        "original": dt.isoformat(),
        "timezone": request.city,
        "converted": converted.isoformat(),
        "local_time": converted.strftime("%H:%M:%S"),
    }
