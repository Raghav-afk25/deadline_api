from datetime import datetime
from app.config import users_col  # users_col mongo collection from config

def consume_request(api_key: str):
    """
    Quota check aur usage update karta hai.
    Returns: (ok: bool, info: str)
    """
    user = users_col.find_one({"api_key": api_key})
    if not user:
        return False, "invalid_api_key"

    today = datetime.utcnow().strftime("%Y-%m-%d")
    usage = user.get("usage", {})
    today_usage = usage.get(today, 0)

    daily_limit = user.get("daily_limit", 1000)
    monthly_limit = user.get("monthly_limit", 20000)

    # ✅ Daily check
    if today_usage >= daily_limit:
        return False, "daily_quota_exceeded"

    # ✅ Monthly check
    month = today[:7]  # "YYYY-MM"
    monthly_usage = user.get("monthly_usage", {})
    month_usage = monthly_usage.get(month, 0)
    if month_usage >= monthly_limit:
        return False, "monthly_quota_exceeded"

    # ✅ Update usage
    usage[today] = today_usage + 1
    monthly_usage[month] = month_usage + 1
    users_col.update_one(
        {"api_key": api_key},
        {"$set": {"usage": usage, "monthly_usage": monthly_usage}}
    )

    return True, "ok"
