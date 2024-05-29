from datetime import date, datetime
from pydantic import BaseModel
from typing import  Optional

from app.models.front_desks import FrontDeskStatus, ParcelType, ReceivedCondition
from app.schemas.customers import CustomerSchema

class FrontDeskCreate(BaseModel):
    customer_id: int
    courier_name: str
    date_of_received: datetime
    parcel_received: ParcelType
    received_condition: ReceivedCondition
    temperature:str
    deparment_id:int
    status: FrontDeskStatus

class FrontDeskSchema(FrontDeskCreate):
    id: int
    customer: Optional[CustomerSchema]
    