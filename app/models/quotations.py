from decimal import Decimal
from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    ForeignKey,
    Boolean,
    Table,
    func,
    UUID,
    Date,
    DateTime,
    Text,
)
from typing import Any, List, Optional
from datetime import date, datetime

from sqlalchemy.orm import mapped_column, Mapped, relationship, joinedload, Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models import Base
from app.models.customers import Customer
from app.models.samples import TestingParameter

class Quotation(Base):
    __tablename__ = "quotations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quotation_code: Mapped[str] = mapped_column(String, nullable=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey(Customer.id))
    sub_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    sgst: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    cgst: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    discount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    grand_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    status: Mapped[str] = mapped_column(String, default="Draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    created_by: Mapped[int] = mapped_column(Integer, nullable=True)
    updated_by: Mapped[int] = mapped_column(Integer, nullable=True)

    # customer: Mapped[Customer] = relationship("Customer", back_populates="quotations")
    test_parameters: Mapped[List["QuotationTestParameter"]] = relationship("QuotationTestParameter", back_populates="quotation", cascade="all, delete-orphan")

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions).order_by(desc(cls.id))
        _result = await database_session.execute(_stmt)
        return _result.scalars().all()
    
    @classmethod
    async def get_all_pagination(
        cls,
        database_session: AsyncSession,
        where_conditions: list[Any],
        page: int,
        page_size: int,
        search: Optional[str] = None,
    ):
        query = select(cls).where(*where_conditions)

        if search:
            search_filter = (
                (cls.quotation_code.ilike(f"%{search}%"))
                | (cls.status.ilike(f"%{search}%"))
                | (Customer.name.ilike(f"%{search}%"))
            )
            query = query.join(Customer).filter(search_filter)

        total_count = await database_session.scalar(
            select(func.count()).select_from(query.subquery())
        )

        query = query.order_by(desc(cls.id)).offset((page - 1) * page_size).limit(page_size)
        result = await database_session.execute(query)
        items = result.scalars().all()

        return {
            "items": items,
            "total": total_count,
            "page": page,
            "page_size": page_size,
        }
    

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()

    async def update_quotation(self, updated_data):
        for field, value in updated_data.items():
            setattr(self, field, value)

    async def create_workflow(self, db_session: AsyncSession, current_user: dict):
        workflow = QuotationWorkflow(
            quotation_id=self.id,
            quotation_status_id=2,
            status="In Progress",
            created_by=current_user["id"],
            updated_by=current_user["id"],
        )
        db_session.add(workflow)
        await db_session.flush()

    async def create_history(self, db_session: AsyncSession, current_user: dict, history_data: dict):
        history = QuotationHistory(**history_data)
        db_session.add(history)
        await db_session.flush()


class QuotationTestParameter(Base):
    __tablename__ = "quotation_test_parameters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quotation_id: Mapped[int] = mapped_column(Integer, ForeignKey(Quotation.id, ondelete="CASCADE"))
    test_parameter_id: Mapped[int] = mapped_column(Integer, ForeignKey(TestingParameter.id))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
    quotation: Mapped[Quotation] = relationship("Quotation", back_populates="test_parameters")
    test_parameter: Mapped[TestingParameter] = relationship("TestingParameter")

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions).order_by(desc(cls.id))
        _result = await database_session.execute(_stmt)
        return _result.scalars().all()

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()

    async def update_quotation_test_parameter(self, updated_data):
        for field, value in updated_data.items():
            setattr(self, field, value)


class QuotationWorkflow(Base):
    __tablename__ = "quotation_workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quotation_id: Mapped[int] = mapped_column(Integer, ForeignKey(Quotation.id, ondelete="CASCADE"))
    quotation_status_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)
    assigned_to: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    created_by: Mapped[int] = mapped_column(Integer)
    updated_by: Mapped[int] = mapped_column(Integer)

    quotation: Mapped[Quotation] = relationship("Quotation")


class QuotationHistory(Base):
    __tablename__ = "quotation_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quotation_id: Mapped[int] = mapped_column(Integer, ForeignKey(Quotation.id, ondelete="CASCADE"))
    from_status_id: Mapped[int] = mapped_column(Integer)
    to_status_id: Mapped[int] = mapped_column(Integer)
    assigned_to: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    created_by: Mapped[int] = mapped_column(Integer)

    quotation: Mapped[Quotation] = relationship("Quotation")
