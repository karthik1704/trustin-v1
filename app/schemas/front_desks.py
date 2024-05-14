from datetime import date
from pydantic import BaseModel
from typing import  Optional

class FrontDeskCreate(BaseModel):
    customer_id: int
    courier_name: str
    date_of_received: date

class FrontDeskSchema(BaseModel):
    id: int
    customer_id: int
    courier_name: str
    date_of_received: date
    