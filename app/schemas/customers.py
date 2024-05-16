from typing import List
from pydantic import BaseModel, EmailStr

from datetime import date
from app.models.customers import MarketingStatus


class ContactPersonCreate(BaseModel):
    person_name: str
    designation: str
    mobile_number: str
    landline_number: str
    contact_email: str


class CustomerCreate(BaseModel):
    company_name: str
    customer_address_line1: str
    customer_address_line2: str
    city: str
    state: str
    pincode_no: str
    website: str
    email: EmailStr
    nature_of_business: str
    product_details: str
    market: str
    regulatory: str
    pan: str
    gst: str

    contact_persons: List[ContactPersonCreate]


class CustomerFollowupCreate(BaseModel):

    customer_id: int
    product_id: int
    marketing_status: MarketingStatus
    assign_to: int
    date: date
    remarks: str


class CustomerSchema(BaseModel):
    id: int
    company_name: str
    customer_address_line1: str | None
    customer_address_line2: str | None
    city: str | None
    state: str | None
    pincode_no: str | None
    website: str | None
    email: EmailStr | str | None
    nature_of_business: str | None
    product_details: str | None
    market: str | None
    regulatory: str | None
    pan: str | None
    gst: str | None
