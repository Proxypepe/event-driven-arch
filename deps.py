from redis_om import get_redis_connection


def get_redis_con():
    return get_redis_connection(
        host='localhost',
        port=6379,
        decode_responses=True
    )
