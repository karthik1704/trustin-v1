from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    DateTime,
    func,
    Enum,
    Text,
    DECIMAL
)
import datetime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.models import Base
from enum import Enum as PyEnum
from .test_request_forms import testtype_association_table, TRF

if TYPE_CHECKING:
    from .test_request_forms import  TRF
    from .branches import Branch
    from .customers  import CustomerFollowUp
    from .test_request_forms  import TestingDetail

class Product(Base):
    __tablename__ = "products"
    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    branch_id:Mapped[int] = mapped_column(ForeignKey("branches.id"))

    product_code :Mapped[str]
    product_name :Mapped[str]
    description:Mapped[str] = mapped_column(Text)
    
    created_at:Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:Mapped[datetime.datetime] =  mapped_column(DateTime(timezone=True), onupdate=func.now())


    branch:Mapped['Branch'] = relationship( back_populates='products')
    parameters:Mapped['TestingParameter'] = relationship(back_populates="product")
    trfs:Mapped['TRF'] = relationship( back_populates='product')
    followups:Mapped['CustomerFollowUp'] = relationship( back_populates="product")

class TestType(Base):
    __tablename__ = "testtypes"
    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name:Mapped[str]
    description:Mapped[Optional[str]] = mapped_column(Text)

    created_at:Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:Mapped[datetime.datetime] =  mapped_column(DateTime(timezone=True), onupdate=func.now())

    parameters:Mapped[List['TestingParameter']] = relationship(back_populates="test_type" )
    trfs:Mapped['TRF'] = relationship( secondary=testtype_association_table, back_populates='test_types') # work needed

class TestingParameter(Base):
    __tablename__ = "testingparameters"
    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)

    branch_id:Mapped[int] = mapped_column( ForeignKey("branches.id"))
    test_type_id:Mapped[int] = mapped_column( ForeignKey("testtypes.id"))
    product_id:Mapped[int] = mapped_column( ForeignKey("products.id"))
    
    parameter_code :Mapped[str]
    testing_parameters:Mapped[str]
    amount:Mapped[Decimal] = mapped_column(DECIMAL(precision=19, scale=4))
    method_or_spec  :Mapped[str]

    group_of_test_parameters :Mapped[str] = mapped_column(Text)
    created_at:Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:Mapped[datetime.datetime] =  mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    
    branch :Mapped['Branch'] = relationship(back_populates="parameters" )
    test_type :Mapped['TestType'] = relationship(back_populates="parameters" )
    product :Mapped['Product'] = relationship(back_populates="parameters")
    test_details :Mapped[List['TestingDetail']] = relationship( back_populates='parameter')