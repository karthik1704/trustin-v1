from pydantic import BaseModel, EmailStr
# from ..models.users import RoleType
from typing import List, Optional


class UserCreate(BaseModel):
    first_name:str
    last_name:str
    email: EmailStr
    password: str
    password2: str
    phone: str
    role_id:int 
    department_id:int
    qa_type_id : Optional[int]


class UserUpdate(BaseModel):
    first_name:str
    last_name:str
    email: EmailStr
    phone: str
    department_id:int
    qa_type_id : Optional[int]


class ForgotPassword(BaseModel):
    password: str
    password2: str


class ChangePassword(BaseModel):
    current_password: str
    password: str
    password2: str

class Token(BaseModel):
    access_token:str
    token_type: str

class UserSchema(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    department : Optional[str]

class RoleSchema(BaseModel):
    id: int
    name: str

class DepartmentSchema(BaseModel):
    id: int
    name: str
    


