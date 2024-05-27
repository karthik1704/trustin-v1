from datetime import date, datetime
from pydantic import BaseModel
from typing import  Optional

from app.models.front_desks import FrontDeskStatus, ParcelType, SampleCondition
from app.schemas.customers import CustomerSchema

class FrontDeskCreate(BaseModel):
    customer_id: int
    courier_name: str
    date_of_received: datetime
    product_received: ParcelType
    sample_condition: SampleCondition
    temperature:str
    deparment_id:int
    status: FrontDeskStatus

class FrontDeskSchema(BaseModel):
    id: int
    customer_id: int
    courier_name: str
    date_of_received: datetime
    status:str
    customer: Optional[CustomerSchema]
    