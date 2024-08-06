from decimal import Decimal
from pydantic import BaseModel
from typing import  List, Optional

class ProductCreate(BaseModel):
    product_name : str
    description : str | None

class ProductSchema(BaseModel):
    id: int
    product_code : str
    product_name : str


class TestTypeCreate(BaseModel):
    name: str
    description:str

class Parameters(BaseModel):
    testing_parameters:str
    amount : Decimal
    group_of_test_parameters : str | None

class MethodAndParam(BaseModel):
    method_or_spec:str
    parameters : List[Parameters] 

class TestParameterCreate(BaseModel):
    test_type_id : int
    product_id : Optional[int]
    methods: List[MethodAndParam]
