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

class Department(str, PyEnum):
    MECH = 'MECH'
    MICRO = 'MICRO'
    


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
    department = Column(Enum(Department), nullable=True)
    
    assingee = relationship("CustomerFollowUp", back_populates="marketing_user")
    sample_assignee = relationship("Sample", foreign_keys="[Sample.assigned_to]", back_populates="assignee")
    # sample_created = relationship("Sample", foreign_keys="[Sample.created_by]", back_populates="created")
