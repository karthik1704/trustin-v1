from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func, Enum
from sqlalchemy.orm import relationship
from app.models import Base
from enum import Enum as PyEnum

class RoleType(str, PyEnum):
    HOD = 'HOD'
    MARKETING = 'MARKETING'
    ADMIN = 'ADMIN'
    MANAGEMENT = 'MANAGEMENT'
    ANALYST = 'ANALYST'


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

    phone = Column(String)

    date_joined = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean(), default=False)
    is_staff = Column(Boolean(), default=False)
    is_superuser = Column(Boolean(), default=False)

    role = Column(Enum(RoleType), default=RoleType.ADMIN)
    
    assingee = relationship("CustomerFollowUp", back_populates="marketing_user")
