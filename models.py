from redis_om import HashModel
from deps import get_redis_con
from pydantic import BaseModel

redis = get_redis_con()


class Delivery(HashModel):
    budget: int = 0
    notes: str = ''

    class Meta:
        database = redis


class Event(HashModel):
    delivery_id: str = None
    type: str
    data: str

    class Meta:
        database = redis
