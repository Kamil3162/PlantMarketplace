import redis


class RedisManager:
    def __init__(self):
        self.client = redis.Redis(
            host="gateway-redis"
        )
        self.prefix = "user-session"

    def insert_data(self, user_data: dict):
        self.client.ping()

        key = self.build_key(self.prefix, user_data['user_id'])

        self.client.hset(
            key,
            mapping=user_data
        )
        print("inserted data into redis")


    def build_key(self, prefix: str, user_id: int):
        return f"{prefix}:{user_id}"

    def get_data(self, user_id: int):
        key = self.build_key(self.prefix, user_id)
        print(self.client.hgetall())

        print("output data from redis")

