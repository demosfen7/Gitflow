from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import FastAPI, HTTPException

app = FastAPI()


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


@app.get("/health", summary="Health Check")
def health():
    return {"status": "ok"}
