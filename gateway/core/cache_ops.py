import redis

class CacheData:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='redis',
            port=6379,
            db=0
        )
        self.blocked_user = "blocked-"
        self.bann
    def assign_blocked_token(self, token):
        name = f"{self.blocked_user}{token}"
        self.redis_client.hset(name=name, value=token)
        return True

