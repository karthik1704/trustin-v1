from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func, Enum
from sqlalchemy.orm import relationship
from app.models import Base

class Branch(Base):
    __tablename__ = "branches"
    id = Column(Integer, primary_key=True)
    branch_name = Column(String)
    address_line1 = Column(String)
    address_line2 = Column(String)
    mobile_number =Column(String)
    landline_number = Column(String)
    email = Column(String)
    pan_no = Column(String)
    cin = Column(String)
    gstin = Column(String)
    bank_details = Column(String)
    ifsc_code = Column(String)

    products = relationship('Product', back_populates='branch')
    parameters = relationship('TestingParameter',back_populates="branch" )
    trfs = relationship('TRF', back_populates='branch')
