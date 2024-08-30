import datetime
from typing import Optional
from sqlalchemy import ForeignKey, String, Boolean, Text, TIMESTAMP
from sqlalchemy.orm import mapped_column,Mapped, relationship
from datetime import datetime,UTC, timezone

from app.models import Base
from app.models.registrations import Sample
from app.models.users import User


class EmailStatus(Base):
    __tablename__ = "email_status"

    id:Mapped[int]  = mapped_column(primary_key=True, index=True)
    recipient:Mapped[str] = mapped_column(String, nullable=False)
    sample_id:Mapped[Optional[int]]  = mapped_column(ForeignKey(Sample.id), nullable=True) 
    subject:Mapped[str] = mapped_column(String, nullable=False)
    sent:Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reason:Mapped[str] = mapped_column(Text, nullable=True)
    timestamp:Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.now(tz=timezone.utc), nullable=False)
    sent_by:Mapped[int] = mapped_column(ForeignKey(User.id))

    sample = relationship("Sample", back_populates="emails")
    emailed_user = relationship('User', back_populates='email_statuses', lazy="selectin")