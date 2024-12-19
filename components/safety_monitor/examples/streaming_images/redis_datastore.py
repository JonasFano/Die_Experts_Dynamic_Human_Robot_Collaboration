import redis
from enum import Enum


class Variables(Enum):
    ShowFixture = "show_fixture"
    ShowText = "show_text"
    ShowPoints = "show_points"


class RedisDataStore:
    # Connect to Redis
    def __init__(self):
        self.redis_client = redis.Redis(
            host="localhost", port=6379, decode_responses=True
        )

    def read_variable(self, variable_name: str):
        value = self.redis_client.get(variable_name)
        if value is None:
            raise Exception(status_code=404, detail="Variable not found")
        return {"variable_name": variable_name, "value": value}

    def update_variable(self, variable_name: str, value: str):
        self.redis_client.set(variable_name, value)
        return {"variable_name": variable_name, "updated_value": value}
