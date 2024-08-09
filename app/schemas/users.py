import re
from pydantic import BaseModel, EmailStr, Field, field_validator, validator

# from ..models.users import RoleType
from typing import List, Optional


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: Optional[EmailStr] = Field(None, description="Invalid E-mail")
    password: str
    password2: str
    phone: str
    designation: str
    role_id: int
    department_id: int
    qa_type_id: Optional[int] | None

    @field_validator("username")
    def validate_username(cls, value):
        if len(value) < 3:
            raise ValueError("Username must be at least 4 characters long")
        if len(value) > 20:
            raise ValueError("Username must be at most 20 characters long")
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValueError(
                "Username can only contain letters, numbers, and underscores"
            )
        return value
    
    @field_validator("email", mode="before")
    def validate_email(cls, value):
        if value == "":
            return None
        return value


class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: Optional[EmailStr] = None
    phone: str
    designation: str
    department_id: int
    qa_type_id: Optional[int]

    @field_validator("username")
    def validate_username(cls, value):
        if len(value) < 3:
            raise ValueError("Username must be at least 4 characters long")
        if len(value) > 20:
            raise ValueError("Username must be at most 20 characters long")
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValueError(
                "Username can only contain letters, numbers, and underscores"
            )
        return value

    @field_validator("email", mode="before")
    def validate_email(cls, value):
        if value == "":
            return None
        return value


class ForgotPassword(BaseModel):
    password: str
    password2: str


class ChangePassword(BaseModel):
    current_password: str
    password: str
    password2: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserSchema(BaseModel):
    id: Optional[int]
    first_name: Optional[str]
    last_name: Optional[str]
    username:Optional[str]
    designation:Optional[str]
    # department_id : Optional[int]
    # role_id : Optional[int]
    # qa_type_id : Optional[int]



class RoleSchema(BaseModel):
    id: int
    name: str


class DepartmentSchema(BaseModel):
    id: int
    name: str

class UserListSchema(UserSchema):
    role: Optional[RoleSchema]
    department: Optional[DepartmentSchema]