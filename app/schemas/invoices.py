from datetime import datetime 
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel

from app.schemas.customers import CustomerSchema


class InvoiceSchema(BaseModel):
    id: Optional[int]
    invoice_code: Optional[str]
    invoice_type: str
    customer_id: int
    customer_address: str
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

    currency: str
    tested_type: str

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

class InvoiceDetailSchema(InvoiceSchema):

    invoice_parameters:Optional[List[InvoiceTestParameterSchema]]

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
    parameters:Optional[List[InvoiceTestParameterCreate]]


class InvoiceTestParameterUpdate(BaseModel):
    id:int
    test_parameter: str
    sac: str
    testing_charge: Decimal
    total_testing_charge: Decimal

class InvoiceUpdate(BaseModel):
    invoice_type: str
    customer_id: int
    customer_address: str
    customer_email: str
    customer_gst: str
    customer_ref_no: str
    quotation_ref_no: str
    sample_id_nos: str
    sub_total: Decimal
    grand_total: Decimal
    sgst: Optional[Decimal]
    cgst: Optional[Decimal]

    currency: str
    tested_type: str

    parameters:list[InvoiceTestParameterUpdate]


