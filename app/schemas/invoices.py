from datetime import datetime 
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel

from app.schemas.customers import CustomerSchema
from app.schemas.users import DepartmentSchema, RoleSchema, UserSchema


class InvoiceSchema(BaseModel):
    id: Optional[int]
    invoice_code: Optional[str]
    invoice_mode: str  # "INVOICE" | "PERFORMA_INVOICE"
    invoice_type: str
    customer_id: int
    customer_address: str
    lut_arn: str | None
    status_id: Optional[int]
    customer_email: str
    customer_gst: str
    customer_ref_no: str
    quotation_ref_no: str
    sample_id_nos: str
    sub_total: Decimal
    grand_total: Decimal
    discount: Decimal
    sgst: Optional[Decimal]
    cgst: Optional[Decimal]
    igst: Optional[Decimal]
    note: Optional[str]
    currency: str
    tested_type: str
    contact_person_name: Optional[str]
    contact_phone: Optional[str]    
    authorized_sign_id: Optional[int]
    authorized_sign: Optional[UserSchema]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: int
    updated_by: int

    customer: Optional[CustomerSchema]

class InvoiceSchemaWithPagination(BaseModel):
    data: List[InvoiceSchema]
    page: int
    size: int
    total:int
    

class InvoiceTestParameterSchema(BaseModel):
    id: int
    
    test_parameter: str
    sac: str
    no_of_tested: str
    testing_charge: Decimal
    total_testing_charge: Decimal


class InvoiceStatusSchema(BaseModel):
    id: int
    name: str


class InvoiceWorkflowSchema(BaseModel):
    id: int
    invoice_status_id: int
    assigned_to: Optional[int]
    status: str
    # assignee: Optional[UserSchema]
    department: Optional[DepartmentSchema]
    role: Optional[RoleSchema]
    invoice_status: Optional[InvoiceStatusSchema]
    updated_at: datetime


class InvoiceHistorySchema(BaseModel):
    id: int
    from_status_id: int
    to_status_id: int
    assigned_to: Optional[int]
    comments: Optional[str]
    created_at: datetime
    created_by: int
    from_status: Optional[InvoiceStatusSchema]
    to_status: Optional[InvoiceStatusSchema]
    # assignee: Optional[UserSchema]
    created_by_user: Optional[UserSchema]


class InvoiceDetailSchema(InvoiceSchema):

    invoice_parameters:Optional[List[InvoiceTestParameterSchema]]
    invoice_workflows: Optional[List[InvoiceWorkflowSchema]]
    invoice_history: Optional[List[InvoiceHistorySchema]]
    status_data: Optional[InvoiceStatusSchema]
    # assignee: Optional[UserSchema]
#
class InvoiceTestParameterCreate(BaseModel):
    test_parameter: str
    sac: str
    no_of_tested: int
    testing_charge: Decimal



class InvoiceCreate(BaseModel):
    invoice_type: str
    customer_id: int
    customer_address: str
    customer_email: str
    customer_gst: str
    customer_ref_no: str
    quotation_ref_no: str
    sample_id_nos: str
    discount: Optional[Decimal] =None
    currency: str
    tested_type: str
    contact_person_name: Optional[str]
    contact_phone: Optional[str]
    invoice_mode: str  # "INVOICE" | "PERFORMA_INVOICE"
    parameters:Optional[List[InvoiceTestParameterCreate]]


class InvoiceTestParameterUpdate(BaseModel):
    id: int | str
    test_parameter: str
    sac: str
    testing_charge: Decimal
    no_of_tested: int

class InvoiceUpdate(BaseModel):
    invoice_type: str
    customer_id: int
    customer_address: str
    customer_email: str
    customer_gst: str
    customer_ref_no: str
    quotation_ref_no: str
    sample_id_nos: str
    contact_person_name: Optional[str]
    contact_phone: Optional[str]
    
   

    currency: str
    tested_type: str

    parameters:List[InvoiceTestParameterUpdate]



class PatchInvoice(BaseModel):
    nabl_logo:Optional[bool] = None
    status: Optional[str] | None
    status_id: Optional[int] | None
    assigned_to: Optional[int] | None = None
    comments: Optional[str] | None
    lut_arn:Optional[str] | None = None
    note:Optional[str] | None = None
    authorized_sign_id: Optional[int] | None = None
   
