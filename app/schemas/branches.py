from pydantic import BaseModel, EmailStr


class Branch(BaseModel):
    branch_name: str
    address_line1: str
    address_line2: str
    mobile_number: str
    landline_number: str
    email: EmailStr
    pan_no: str
    cin: str
    gstin: str
    bank_details: str
    ifsc_code: str

class BranchCreate(BaseModel):
    pass
