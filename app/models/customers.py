import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from app.models import Base
from enum import Enum as PyEnum
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .test_request_forms import TRF
    from .users import User
    from .samples import Product


class MarketingStatus(PyEnum):
    NONE = ''
    MAIL_SENT = 'MAIL_SENT'
    ENQUIRES_RECEIVED = 'ENQUIRES_RECEIVED'
    QUOTE_SENT = 'QUOTE_SENT'
    MARKETING_PLAN = 'MARKETING_PLAN'  # Fix typo in 'MARKETINT_PLAN'
    SITE_VISITED = 'SITE_VISITED'
    LAB_VISIT_PLAN = 'LAB_VISIT_PLAN'
    LAB_VISITED = 'LAB_VISITED'
    FOLLOWUP = 'FOLLOWUP'
    WON = 'WON'
    WORK_IN_PROGRESS = 'WORK_IN_PROGRESS'  # Updated to use underscores
    HOLD = 'HOLD'
    LOST = 'LOST'
    SAMPLE_RECEIVED = 'SAMPLE_RECEIVED'


class Customer(Base):
    __tablename__ = "customers"
    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)

    # branch = models.ForeignKey(Branch, related_name='customer_branch',on_delete=models.CASCADE)
    
    customer_code :Mapped[str] = mapped_column(unique=True)
    company_name :Mapped[str]
    company_id :Mapped[str]
    customer_address_line1 :Mapped[str]
    customer_address_line2 :Mapped[Optional[str]]
    city :Mapped[str]
    state :Mapped[str]
    pincode_no :Mapped[str]
    website :Mapped[Optional[str]]
    email:Mapped[str] = mapped_column(unique=True)


    nature_of_business :Mapped[Optional[str]]
    product_details :Mapped[Optional[str]]
    market :Mapped[Optional[str]]
    regulatory :Mapped[Optional[str]]
    pan :Mapped[Optional[str]]
    gst :Mapped[Optional[str]]

 
    created_at:Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:Mapped[datetime.datetime] =  mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    contact_persons:Mapped[List['ContactPerson']] = relationship( back_populates="customer")
    followups:Mapped[List['CustomerFollowUp']] = relationship( back_populates="customer")
    trfs:Mapped[List['TRF']] = relationship( back_populates='customer')


class ContactPerson(Base):
    __tablename__ = "contactpersons"
    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)

    customer_id:Mapped[int] = mapped_column(ForeignKey('customers.id'))
    
    
    person_name :Mapped[str]
    designation :Mapped[Optional[str]]
    mobile_number :Mapped[str]
    landline_number:Mapped[Optional[str]]
    contact_email:Mapped[str]

    created_at:Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:Mapped[datetime.datetime] =  mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    customer:Mapped['Customer'] = relationship( back_populates="contact_persons")


   

class CustomerFollowUp(Base):
    __tablename__ = "customerfollowups"
    id:Mapped[int] = mapped_column( primary_key=True, autoincrement=True, index=True)

    customer_id:Mapped[int] =mapped_column( ForeignKey('customers.id'))
    product_id:Mapped[int] =mapped_column( ForeignKey('products.id'))

    marketing_status:Mapped[MarketingStatus]
    assign_to:Mapped[int] = mapped_column( ForeignKey('users.id'))
    
    date:Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    remarks:Mapped[str] = mapped_column(Text)


    customer:Mapped['Customer'] = relationship( back_populates="followups")
    marketing_user:Mapped['User'] = relationship( back_populates="assingee")
    
    trf_id:Mapped[int] = mapped_column(ForeignKey('test_request_forms.id'), unique=True)
    trf:Mapped['TRF'] = relationship( back_populates="followup")

    product:Mapped['Product'] = relationship( back_populates="followups")

    
    created_at:Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:Mapped[datetime.datetime] =  mapped_column(DateTime(timezone=True), onupdate=func.now())

