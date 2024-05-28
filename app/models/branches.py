from typing import Any, List, TYPE_CHECKING, Optional

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models import Base

if TYPE_CHECKING:
    from .samples import Product, TestingParameter
    from app.models.test_request_forms import TRF


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column( primary_key=True)
    branch_name: Mapped[str]  = mapped_column(unique=True, index=True)
    address_line1: Mapped[Optional[str]]  
    address_line2: Mapped[Optional[str]]  
    mobile_number: Mapped[Optional[str]]  
    landline_number: Mapped[Optional[str]]  
    email :Mapped[Optional[str]]  
    pan_no :Mapped[Optional[str]]  
    cin :Mapped[Optional[str]]  
    gstin :Mapped[Optional[str]]  
    bank_details :Mapped[Optional[str]]  
    ifsc_code :Mapped[Optional[str]]  

    products:Mapped[List['Product']]   = relationship( back_populates='branch')
    parameters:Mapped[List['TestingParameter']] = relationship(back_populates="branch" )
    # trfs:Mapped[List['TRF']] = relationship( back_populates='branch')

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

    def update_branch(self, updated_data):

        for field, value in updated_data.items():
            setattr(self, field, value) if value else None