from typing import Optional
from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    email: EmailStr
    subject: str
    message: str
    attachment: Optional[str] = None
    filename:  Optional[str] = None