from decimal import Decimal
from locale import currency
from sqlalchemy import (
    Column,
    Integer,
    DECIMAL,
    Nullable,
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

# from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column, Mapped, relationship, joinedload, Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models import Base
from app.models.customers import Customer
from app.utils import get_unique_code_invoice


class InvoiceStatus(Base):
    __tablename__ = "invoice_status"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departments.id"), nullable=True
    )
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    invoice = relationship("Invoice", back_populates="status_data", lazy="selectin")
    invoice_history_from = relationship(
        "InvoiceHistory",
        back_populates="from_status",
        foreign_keys="[InvoiceHistory.from_status_id]",
    )
    invoice_history_to = relationship(
        "InvoiceHistory",
        back_populates="to_status",
        foreign_keys="[InvoiceHistory.to_status_id]",
    )
    invoice_workflow_status = relationship(
        "InvoiceWorkflow", back_populates="invoice_status", lazy="selectin"
    )

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions).order_by(cls.id)
        _result = await database_session.execute(_stmt)
        return _result.scalars().all()

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_code: Mapped[str] = mapped_column(String, nullable=True)
    invoice_type: Mapped[str]
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey(Customer.id))
    customer_address: Mapped[str] = mapped_column(Text)
    customer_email: Mapped[str]
    customer_gst: Mapped[str]
    customer_ref_no: Mapped[str]
    quotation_ref_no: Mapped[str]
    sample_id_nos: Mapped[str]
    status: Mapped[str] = mapped_column(String, default="Registered", nullable=True)
    sub_total: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False
    )
    grand_total: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False
    )
    discount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=2), nullable=True
    )
    sgst: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=2), nullable=True
    )
    cgst: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=2), nullable=True
    )
    igst: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=2), nullable=True
    )
    status_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(InvoiceStatus.id), nullable=True
    )
    currency: Mapped[str]
    tested_type: Mapped[str]
    lut_arn:Mapped[Optional[str]]
    note:Mapped[Optional[str]]

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    invoice_parameters = relationship(
        "InvoiceTestParameter",
        back_populates="invoice",
        lazy="selectin",
        cascade="all, delete",
    )
    customer = relationship(
        "Customer",
        back_populates="invoices",
        lazy="selectin",
    )
    status_data = relationship("InvoiceStatus", back_populates="invoice", lazy="selectin")
    invoice_history = relationship("InvoiceHistory", back_populates="invoice", lazy="selectin")
    invoice_workflows = relationship("InvoiceWorkflow", back_populates="invoice", lazy="selectin")


    @classmethod
    async def get_all_with_pagination(
        cls,
        database_session: AsyncSession,
        where_conditions: list[Any],
        page: int = 1,
        size: int = 10,
        search: Optional[str] = None,
        sort_by: str = "id",
        sort_order: str = "desc",
    ):
        _stmt = select(cls).where(*where_conditions)

        if search:
            _stmt = _stmt.where(cls.invoice_code.ilike(f"%{search}%"))
        print(sort_by)
        print(sort_order)
        if sort_by and hasattr(cls, sort_by):
            if sort_order == "asc":
                _stmt = _stmt.order_by(getattr(cls, sort_by).asc())
            else:
                _stmt = _stmt.order_by(getattr(cls, sort_by).desc())
        total_query = select(func.count()).select_from(_stmt.subquery())
        total_result = await database_session.execute(total_query)
        total_invoices = total_result.scalar()
        invoices = _stmt.offset((page - 1) * size).limit(size)

        result = await database_session.execute(invoices)
        invoices = result.scalars().all()

        return {
            "data": invoices,
            "total": total_invoices,
            "page": page,
            "size": size,
        }


    @classmethod
    async def generate_next_code(cls, database_session):

        _stmt = select(cls.invoice_code).order_by(desc(cls.invoice_code))
        _result = await database_session.execute(_stmt)
        if _result:
            highest_code = _result.scalars().first()
        if highest_code:
            highest_code_int = int(highest_code.split(f"/")[-1]) + 1
        else:
            highest_code_int = 1001
        # Generate the new code by combining the prefix and the incremented integer
        new_code = get_unique_code_invoice(
            highest_code_int, highest_code
        )  # Adjust the format based on your requirements
        # database_session.close()
        return new_code
    
    @classmethod
    async def get_lut_arn(cls, database_session):
        _stmt = (
            select(cls.lut_arn)
            .where(cls.lut_arn.isnot(None))  # Filter out null values
            .order_by(desc(cls.id))  # Order by descending id to get the latest
        )
        _result = await database_session.execute(_stmt)
        lut_arn = _result.scalars().first()  # Get the first result

        return lut_arn

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

    async def update_invoice(self, updated_data):
        for field, value in updated_data.items():
            setattr(self, field, value)

    async def create_workflow(self, db_session, current_user):
        status_list = await InvoiceStatus.get_all(db_session, [])
        time = datetime.now()
        update_dict = {
            "created_at": time,
            "updated_at": time,
            "created_by": current_user["id"],
            "updated_by": current_user["id"],
        }

        for status in status_list:
            workflow_dict = {
                "invoice_id": self.id,
                "invoice_status_id": status.id,
                "department_id": status.department_id,
                "role_id": status.role_id,
                "assigned_to": (
                    current_user["id"]
                    if status.name == "Edit"
                    else status.user_id
                ),
                "status": (
                    "Done"
                    if status.name == "Edit"
                    else (
                        "In Progress"
                        if status.name == "Approve"
                        else "Yet To Start"
                    )
                ),
            }

            workflow_dict = {**workflow_dict, **update_dict}
            print(workflow_dict)
            workflow = InvoiceWorkflow(**workflow_dict)
            db_session.add(workflow)
            continue

           
        await db_session.commit()

    async def create_history(self, db_session, current_user, history):
        time = datetime.now()
        update_dict = {
            "created_at": time,
            "created_by": current_user["id"],
        }
        history = {**history, **update_dict}
        history = InvoiceHistory(**history)
        db_session.add(history)
        await db_session.commit()




class InvoiceTestParameter(Base):
    __tablename__ = "invoice_test_parameters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(Invoice.id, ondelete="CASCADE"),
    )
    test_parameter: Mapped[str]
    sac: Mapped[str]
    no_of_tested: Mapped[str]
    testing_charge: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False
    )
    total_testing_charge: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    invoice = relationship(
        "Invoice",
        back_populates="invoice_parameters",
    )

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

    def update_invoice_parameters(self, updated_data):
        for field, value in updated_data.items():
            setattr(self, field, value)



class InvoiceHistory(Base):
    __tablename__ = "invoice_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey(Invoice.id))
  
    from_status_id: Mapped[int] = mapped_column(Integer, ForeignKey(InvoiceStatus.id))
    to_status_id: Mapped[int] = mapped_column(Integer, ForeignKey(InvoiceStatus.id))
    assigned_to: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    comments: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    invoice = relationship("Invoice", back_populates="invoice_history")
    assignee = relationship(
        "User",
        back_populates="invoice_history_assignee",
        foreign_keys=[assigned_to],
        lazy="selectin",
    )
    created_by_user = relationship(
        "User",
        back_populates="invoice_history_created",
        foreign_keys=[created_by],
        lazy="selectin",
    )
    from_status = relationship(
        "InvoiceStatus",
        back_populates="invoice_history_from",
        foreign_keys=[from_status_id],
        lazy="selectin",
    )
    to_status = relationship(
        "InvoiceStatus",
        back_populates="invoice_history_to",
        foreign_keys=[to_status_id],
        lazy="selectin",
    )
  




class InvoiceWorkflow(Base):
    __tablename__ = "invoice_workflows"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey(Invoice.id))
    invoice_status_id: Mapped[int] = mapped_column(Integer, ForeignKey(InvoiceStatus.id))
  
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departments.id"), nullable=True
    )
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=True)
    assigned_to: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String, server_default="Yet to start")

    invoice = relationship("Invoice", back_populates="invoice_workflows")
    assignee = relationship(
        "User",
        back_populates="invoice_workflow_assignee",
        foreign_keys=[assigned_to],
        lazy="selectin",
    )
    department = relationship(
        "Department", back_populates="invoice_workflow_department", lazy="selectin"
    )
    role = relationship("Role", back_populates="invoice_workflow_role", lazy="selectin")
    invoice_status = relationship(
        "InvoiceStatus", back_populates="invoice_workflow_status", lazy="selectin"
    )
 


    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars()

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        print("where_conditions", *where_conditions)
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()

    async def update_workflow(self, updated_data):
        for field, value in updated_data.items():
            print(self.id, field, value)
            setattr(self, field, value) if value else None