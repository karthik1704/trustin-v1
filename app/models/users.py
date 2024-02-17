import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    DateTime,
    func,
    Enum,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.models import Base
from enum import Enum as PyEnum

if TYPE_CHECKING:
    from .customers import CustomerFollowUp


class RoleType(str, PyEnum):
    HOD = "HOD"
    MARKETING = "MARKETING"
    ADMIN = "ADMIN"
    MANAGEMENT = "MANAGEMENT"
    ANALYST = "ANALYST"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    first_name: Mapped[str]
    last_name: Mapped[Optional[str]]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    phone: Mapped[str]

    date_joined: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    last_login: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(default=False)
    is_staff: Mapped[bool] = mapped_column(default=False)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    role: Mapped[RoleType] = mapped_column(default=RoleType.ADMIN)

    assingee: Mapped["CustomerFollowUp"] = relationship(back_populates="marketing_user")
