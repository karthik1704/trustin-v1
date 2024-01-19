from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func, Enum, Text
from sqlalchemy.orm import relationship
from app.models import Base
from enum import Enum as PyEnum

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
    id = Column(Integer, primary_key=True)

    # branch = models.ForeignKey(Branch, related_name='customer_branch',on_delete=models.CASCADE)
    
    customer_code =  Column(String)
    company_name =  Column(String)
    company_id =  Column(String)
    customer_address_line1 =  Column(String)
    customer_address_line2 =  Column(String)
    city =  Column(String)
    state =  Column(String)
    pincode_no =  Column(String)
    website =  Column(String)
    email =   Column(String)


    nature_of_business =  Column(String)
    product_details =  Column(String)
    market =  Column(String)
    regulatory =  Column(String)
    pan =  Column(String)
    gst =  Column(String)

    created_at =Column(DateTime(timezone=True), server_default=func.now())
    updated_at =  Column(DateTime(timezone=True), onupdate=func.now())
    
    contact_persons = relationship("ContactPerson", back_populates="customer")
    followups = relationship("CustomerFollowUp", back_populates="customer")
    trfs = relationship('TRF', back_populates='customer')


class ContactPerson(Base):
    __tablename__ = "contactpersons"
    id = Column(Integer, primary_key=True)

    customer_id = Column(Integer, ForeignKey('customers.id'))
    
    
    person_name =Column(String)
    designation =Column(String)
    mobile_number = Column(String)
    landline_number = Column(String)
    email =  Column(String)

    created_at =Column(DateTime(timezone=True), server_default=func.now())
    updated_at =  Column(DateTime(timezone=True), onupdate=func.now())
    
    customer = relationship("Customer", back_populates="contact_persons")


   

class CustomerFollowUp(Base):
    __tablename__ = "customerfollowups"
    id = Column(Integer, primary_key=True)

    customer_id = Column(Integer, ForeignKey('customers.id'))
    product_id = Column(Integer, ForeignKey('products.id'))

    marketing_status = Column(Enum(MarketingStatus), default=MarketingStatus.NONE)
    
    assign_to = Column(Integer, ForeignKey('users.id'))
    
    date = Column(DateTime(timezone=True), default=func.now())

    remarks = Column(Text)


    customer = relationship("Customer", back_populates="followups")
    marketing_user = relationship("User", back_populates="assingee")
    trf_id = Column(Integer, ForeignKey('test_request_forms.id'), unique=True)
    trf = relationship("TRF", back_populates="followup")
    product = relationship("Product", back_populates="followups")

    
    created_at =Column(DateTime(timezone=True), server_default=func.now())
    updated_at =  Column(DateTime(timezone=True), onupdate=func.now())
    

