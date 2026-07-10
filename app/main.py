from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import pytz

app = FastAPI(title="Time Server API")


@app.get("/")
def root():
    return {"message": "Добро пожаловать в Time Server API"}


@app.get("/time")
def get_time():
    return {"time": datetime.now(pytz.UTC).isoformat()}


@app.get("/date")
def get_date():
    return {"date": datetime.now(pytz.UTC).date().isoformat()}


@app.get("/datetime")
def get_datetime():
    return {"datetime": datetime.now(pytz.UTC).isoformat()}


class ConvertRequest(BaseModel):
    time: str
    city: str


@app.post("/convert")
def convert_time(request: ConvertRequest):
    try:
        target_tz = pytz.timezone(request.city)
    except pytz.exceptions.UnknownTimeZoneError:
        raise HTTPException(
            status_code=400,
            detail=f"Неизвестный часовой пояс: {request.city}. Пример: Europe/Moscow",
        )

    try:
        dt = datetime.fromisoformat(request.time)
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат времени. Используйте ISO 8601, например 2026-07-10T12:00:00",
        )

    converted = dt.astimezone(target_tz)
    return {
        "original": dt.isoformat(),
        "timezone": request.city,
        "converted": converted.isoformat(),
        "local_time": converted.strftime("%H:%M:%S"),
    }
