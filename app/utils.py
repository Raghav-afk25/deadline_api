from fastapi import HTTPException
from datetime import datetime
from app.config import users_col

def check_api_key(key: str):
    user = users_col.find_one({"api_key": key})
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    today = datetime.utcnow().strftime("%Y-%m-%d")
    usage = user.get("usage", {})
    today_usage = usage.get(today, 0)

    daily_limit = user.get("daily_limit", 1000)

    if today_usage >= daily_limit:
        raise HTTPException(status_code=429, detail="Daily limit reached")

    # update usage
    usage[today] = today_usage + 1
    users_col.update_one({"api_key": key}, {"$set": {"usage": usage}})
    return user
