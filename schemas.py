from pydantic import BaseModel


class DeliveryBase(BaseModel):
    budget: int = 0
    notes: str = ''


class DeliveryCreate(BaseModel):
    type: str
    data: DeliveryBase


class DeliveryDispatchBase(BaseModel):
    type: str
    delivery_id: str


class DeliveryDispatch(DeliveryDispatchBase, DeliveryCreate):
    ...


class DeliveryStart(DeliveryDispatchBase):
    ...

