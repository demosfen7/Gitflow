from datetime import datetime, timezone

from fastapi import FastAPI

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


@app.get("/health", summary="Health Check")
def health():
    return {"status": "ok"}
