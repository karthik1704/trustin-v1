from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime

class QuotationTestParameterSchema(BaseModel):
    id: int
    quotation_id: int
    test_parameter_id: int
    amount: Decimal

class QuotationSchema(BaseModel):
    id: int
    quotation_code: Optional[str] = None
    customer_id: int
    sub_total: Decimal = Field(default=0)
    sgst: Decimal = Field(default=0)
    cgst: Decimal = Field(default=0)
    discount: Decimal = Field(default=0)
    grand_total: Decimal = Field(default=0)
    status: str = Field(default="Draft")
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    test_parameters: List[QuotationTestParameterSchema] = []

class QuotationCreate(BaseModel):
    customer_id: int
    quotation_code: Optional[str] = None
    discount: Decimal = Field(default=0)
    status: str = Field(default="Draft")
    test_parameters: List[QuotationTestParameterSchema] = []

class QuotationUpdate(BaseModel):
    customer_id: Optional[int] = None
    quotation_code: Optional[str] = None
    discount: Optional[Decimal] = None
    status: Optional[str] = None
    test_parameters: Optional[List[QuotationTestParameterSchema]] = None

class PatchQuotation(BaseModel):
    customer_id: Optional[int] = None
    status: Optional[str] = None
    comments: Optional[str] = None
