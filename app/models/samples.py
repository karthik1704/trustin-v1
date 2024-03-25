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
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.models import Base
from enum import Enum as PyEnum
from .test_request_forms import testtype_association_table

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    branch_id = Column(Integer, ForeignKey("branches.id"))

    product_code = Column(String)
    product_name = Column(String)
    description = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    branch = relationship('Branch', back_populates='products')
    parameters = relationship('TestingParameter',back_populates="product")
    trfs = relationship('TRF', back_populates='product')
    followups = relationship("CustomerFollowUp", back_populates="product")

class TestType(Base):
    __tablename__ = "testtypes"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    parameters = relationship('TestingParameter',back_populates="test_type" )
    trfs = relationship('TRF', secondary=testtype_association_table, back_populates='test_types')
    registration_test_types = relationship('RegistrationTestType',  back_populates='test_type')

class TestingParameter(Base):
    __tablename__ = "testingparameters"
    id = Column(Integer, primary_key=True)

    branch_id = Column(Integer, ForeignKey("branches.id"))
    test_type_id = Column(Integer, ForeignKey("testtypes.id"))
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    
    parameter_code : Mapped[str]= mapped_column(String, nullable=True)
    testing_parameters = Column(String)
    amount = Column(DECIMAL(precision=19, scale=4))
    method_or_spec = Column(String)

    group_of_test_parameters = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    branch = relationship('Branch',back_populates="parameters" )
    test_type = relationship('TestType',back_populates="parameters" )
    product = relationship('Product',back_populates="parameters")
    test_details = relationship('TestingDetail', back_populates='parameter')
    customer = relationship('Customer',back_populates = 'parameters')
    registration_test_parameters = relationship('RegistrationTestParameter',back_populates = 'test_parameter')
    sample_test_parameters = relationship('SampleTestParameter',back_populates = 'test_parameter')

    