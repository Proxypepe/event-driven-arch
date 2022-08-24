import json

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware

from deps import get_redis_con
from models import Delivery, Event
from schemas import DeliveryCreate, DeliveryDispatch
import consumers

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)


def build_state(pk: str) -> dict:
    pks = Event.all_pks()
    all_events = [Event.get(pk) for pk in pks]
    events = [event for event in all_events if event.delivery_id == pk]
    state = {}

    for event in events:
        state = consumers.CONSUMERS[event.type](state, event)

    return state


@app.get('/deliveries/{pk}/status')
async def get_state(pk: str, redis=Depends(get_redis_con)) -> dict:
    state = redis.get(f'delivery:{pk}')
    if state is not None:
        return json.loads(state)

    state = build_state(pk)
    redis.set(f'delivery:{pk}', json.dumps(state))
    return state


@app.post('/deliveries/create')
async def create_delivery(delivery: DeliveryCreate, redis=Depends(get_redis_con)) -> dict:
    new_delivery = Delivery(**delivery.data.dict()).save()
    event = Event(delivery_id=new_delivery.pk, type=delivery.type, data=json.dumps(delivery.data.dict())).save()
    state = consumers.CONSUMERS[event.type]({}, event)
    redis.set(f'delivery:{new_delivery.pk}', json.dumps(state))
    return state


@app.post('/event')
async def dispatch(request: Request):
    body = await request.json()
    delivery_id = body['delivery_id']
    state = await get_state(delivery_id)
    event = Event(delivery_id=delivery_id, type=body['type'], data=json.dumps(body['data'])).save()
    new_state = consumers.CONSUMERS[event.type](state, event)
    redis.set(f'delivery:{delivery_id}', json.dumps(new_state))
    return new_state

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)
