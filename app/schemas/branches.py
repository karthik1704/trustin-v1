from typing import Optional
from pydantic import BaseModel, EmailStr


class Branch(BaseModel):
    branch_name: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    mobile_number: Optional[str]
    landline_number: Optional[str]
    email: Optional[EmailStr]
    pan_no: Optional[str]
    cin: Optional[str]
    gstin: Optional[str]
    bank_details: Optional[str]
    ifsc_code: Optional[str]

class BranchCreate(Branch):
    pass

class BranchSchema(Branch):
    id: int