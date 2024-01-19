from decimal import Decimal
from pydantic import BaseModel


class ProductCreate(BaseModel):
    branch_id: int

    product_code : str
    product_name : str
    description : str


class TestTypeCreate(BaseModel):
    name: str
    description:str

class TestParameterCreate(BaseModel):
    branch_id : int
    test_type_id : int
    product_id : int
    
    parameter_code:str
    testing_parameters:str
    amount : Decimal
    method_or_spec:str

    group_of_test_parameters : str