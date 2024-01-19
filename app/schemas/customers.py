
from typing import List
from pydantic import BaseModel, EmailStr

from datetime import date
from app.models.customers import MarketingStatus

class ContactPersonCreate(BaseModel):
    person_name :str
    designation :str
    mobile_number : str
    landline_number : str
    email : str
    customer_id: int

class CustomerCreate(BaseModel):
    customer_code :str
    company_name :str
    company_id :str
    customer_address_line1 :str
    customer_address_line2 :str
    city :str
    state :str
    pincode_no :str
    website :str
    email : EmailStr
    nature_of_business :str
    product_details :str
    market :str
    regulatory :str
    pan :str
    gst :str

    contact_persons: List[ContactPersonCreate]
  
class CustomerFollowupCreate(BaseModel):

    customer_id : int
    product_id : int
    marketing_status : MarketingStatus
    assign_to : int
    date: date
    remarks: str
    trf_id: int