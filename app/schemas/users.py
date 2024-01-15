from pydantic import BaseModel, EmailStr
from ..models.users import RoleType


class UserCreate(BaseModel):
    first_name:str
    last_name:str
    email: EmailStr
    password: str
    password2: str
    phone: str
    is_staff: bool
    is_superuser:bool
    role:RoleType 


class ForgotPassword(BaseModel):
    password: str
    password2: str


class ChangePassword(BaseModel):
    current_password: str
    password: str
    password2: str