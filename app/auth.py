from fastapi import HTTPException
from app.db import consume_request  # ✅ yeh tumhare quota check ke liye DB function

def check_api_key(key: str):
    ok, info = consume_request(key)
    if not ok:
        code = 429 if info in ("daily_quota_exceeded", "monthly_quota_exceeded") else 403
        raise HTTPException(code, detail=str(info))
    return True
