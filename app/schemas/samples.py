from decimal import Decimal
from pydantic import BaseModel
from typing import  Optional

class ProductCreate(BaseModel):
    branch_id: int
    product_name : str
    description : str

class ProductSchema(BaseModel):
    id: int
    product_code : str
    product_name : str


class TestTypeCreate(BaseModel):
    name: str
    description:str

class TestParameterCreate(BaseModel):
    # branch_id : int
    test_type_id : int
    product_id : Optional[int]
    # customer_id : Optional[int]
    
    # parameter_code:str
    testing_parameters:str
    amount : Decimal
    method_or_spec:str

    group_of_test_parameters : str | None