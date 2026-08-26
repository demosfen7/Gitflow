from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI()


@app.get("/time")
def get_time():
    now = datetime.now(timezone.utc)
    return {
        "utc_time": now.isoformat(),
        "timestamp": now.timestamp(),
    }
