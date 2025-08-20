import time
from fastapi import HTTPException
from app.config import API_KEYS, PLANS

# Store request timestamps
request_logs = {}

def check_rate_limit(api_key: str):
    if api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    plan = API_KEYS[api_key]
    limit = PLANS.get(plan, 5)  # default FREE

    now = time.time()
    window = 60  # seconds

    if api_key not in request_logs:
        request_logs[api_key] = []

    # Purge old requests
    request_logs[api_key] = [t for t in request_logs[api_key] if now - t < window]

    if len(request_logs[api_key]) >= limit:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded ({plan} plan)")

    request_logs[api_key].append(now)
