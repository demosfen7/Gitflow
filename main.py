from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import FastAPI, HTTPException, Query

app = FastAPI()

# Принимаемые форматы строки времени на входе /convert — с двоеточием и с точкой,
# с секундами и без.
_TIME_FORMATS = ["%H:%M:%S", "%H:%M", "%H.%M.%S", "%H.%M"]


@app.get("/", summary="Root")
def root():
    return {"service": "gitflow", "status": "ok"}


@app.get("/time", summary="Get Current Time")
def get_time():
    now = datetime.now(timezone.utc)
    return {
        "utc_time": now.isoformat(),
        "timestamp": now.timestamp(),
    }


@app.get("/date", summary="Get Current Date")
def get_date():
    today = datetime.now(timezone.utc).date()
    return {
        "date": today.isoformat(),
        "year": today.year,
        "month": today.month,
        "day": today.day,
    }


@app.get("/datetime", summary="Get Current Datetime")
def get_datetime():
    now = datetime.now(timezone.utc)
    return {
        "datetime": now.isoformat(),
        "date": now.date().isoformat(),
        "time": now.time().isoformat(),
        "timestamp": now.timestamp(),
    }


@app.get("/timezone/{tz:path}", summary="Convert Time To Timezone")
def convert_timezone(tz: str):
    try:
        zone = ZoneInfo(tz)
    except ZoneInfoNotFoundError:
        raise HTTPException(status_code=404, detail=f"Unknown timezone: {tz}")

    now = datetime.now(zone)
    return {
        "timezone": tz,
        "datetime": now.isoformat(),
        "utc_offset": now.strftime("%z"),
    }


@app.get("/convert", summary="Convert UTC Time To Timezone")
def convert_time(
    time: str = Query(..., description="Время в UTC, например 15:00 или 15.00"),
    tz: str = Query(..., description="Целевой часовой пояс, IANA-имя, например Asia/Yekaterinburg"),
):
    for fmt in _TIME_FORMATS:
        try:
            parsed = datetime.strptime(time, fmt).time()
            break
        except ValueError:
            continue
    else:
        raise HTTPException(status_code=400, detail=f"Unrecognized time format: {time!r}. Use HH:MM or HH:MM:SS")

    try:
        zone = ZoneInfo(tz)
    except ZoneInfoNotFoundError:
        raise HTTPException(status_code=404, detail=f"Unknown timezone: {tz}")

    utc_dt = datetime.combine(datetime.now(timezone.utc).date(), parsed, tzinfo=timezone.utc)
    converted = utc_dt.astimezone(zone)

    return {
        "input_utc_time": time,
        "timezone": tz,
        "converted_time": converted.strftime("%H:%M"),
        "converted_datetime": converted.isoformat(),
        "utc_offset": converted.strftime("%z"),
    }


@app.get("/health", summary="Health Check")
def health():
    return {"status": "ok"}
