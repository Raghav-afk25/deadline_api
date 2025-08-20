import time
from collections import defaultdict
from app.config import API_KEYS

class RateLimiter:
    def __init__(self):
        self.daily_count = defaultdict(int)
        self.monthly_count = defaultdict(int)
        self.last_reset_day = int(time.strftime("%j"))  # day of year
        self.last_reset_month = int(time.strftime("%m"))

    def reset_if_needed(self):
        current_day = int(time.strftime("%j"))
        current_month = int(time.strftime("%m"))

        if current_day != self.last_reset_day:
            self.daily_count.clear()
            self.last_reset_day = current_day

        if current_month != self.last_reset_month:
            self.monthly_count.clear()
            self.last_reset_month = current_month

    def allow_request(self, key: str) -> bool:
        self.reset_if_needed()
        if key not in API_KEYS:
            return False

        daily_limit, monthly_limit = API_KEYS[key]

        if self.daily_count[key] >= daily_limit:
            return False
        if self.monthly_count[key] >= monthly_limit:
            return False

        self.daily_count[key] += 1
        self.monthly_count[key] += 1
        return True
