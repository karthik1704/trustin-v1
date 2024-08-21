from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.schemas.users import UserSchema


class EmailSchema(BaseModel):
    email: EmailStr
    sample_id: Optional[int] = None
    # subject: str
    # message: str
    email_type: str
    attachment: Optional[str] = None
    filename:  Optional[str] = None


class EmailStatusSchema(BaseModel):
    id:int
    recipient:str
    sample_id:int
    subject:str
    sent:bool
    sent_by:int
    timestamp:datetime
    reason:Optional[str]
    emailed_user:Optional[UserSchema]