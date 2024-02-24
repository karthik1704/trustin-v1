import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime,Date, func,  UUID
from typing import Any
import datetime
# from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column, Mapped, relationship, joinedload,Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Base, Branch, TRF, Customer, TestingParameter
from enum import Enum as PyEnum




class Registration(Base):
    __tablename__ = "registrations"
    id : Mapped[int]= mapped_column(Integer, primary_key=True)
    branch_id : Mapped[int] = mapped_column(Integer, ForeignKey(Branch.id))
    trf_id  : Mapped[int]  = mapped_column(Integer, ForeignKey(TRF.id))
    company_id  : Mapped[int] =  mapped_column(Integer, ForeignKey(Customer.id))
    company_name  : Mapped[int] =  mapped_column(String)
    customer_address_line1  : Mapped[int] =  mapped_column(String)
    customer_address_line2  : Mapped[int] =  mapped_column(String)
    city  : Mapped[int] =  mapped_column(String)
    state  : Mapped[int] =  mapped_column(String)
    pincode_no  : Mapped[int]  =  mapped_column(String)
    gst  : Mapped[int] =  mapped_column(String)
    date_of_registration  : Mapped[DateTime] =mapped_column(DateTime(timezone=True), server_default=func.now())
    date_of_received  : Mapped[DateTime] =mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at : Mapped[DateTime]  =mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at  : Mapped[DateTime] =  mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    test_type  : Mapped[str] =  mapped_column(String)
    product : Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))

    trf = relationship("TRF", back_populates="registrations")
    batches = relationship("Batch", back_populates="registration", lazy="selectin")

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars()

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()

    def update_registration(self, updated_data):
        
        for field, value in updated_data.items():
            setattr(self, field, value) if value else None

    async def update_batches(self, database_session: AsyncSession, batches_data, current_user):
        print("update batches")
        time = datetime.datetime.now()
        for batch_data in batches_data:
            batch_id = batch_data.pop('id', None)
            batch = None
            if batch_id:
                batch = await Batch.get_one(database_session,[Batch.id == batch_id])
                print(batch)
            if batch:
                print("u[date]")
                update_dict = {
                        "updated_at" : time,
                        "updated_by" : current_user["id"],
                    }
                batch_data = {**batch_data, **update_dict}
                batch.update_batch(batch_data)
            else:
                print("create")
                print(batch_data)
                
                update_dict = {
                        "created_at" :time ,
                        "updated_at" : time,
                        "created_by" : current_user["id"],
                        "updated_by" : current_user["id"],
                    }
                batch_data = {**batch_data, **update_dict}
                batch = Batch(**batch_data, registration_id=self.id)
                Batch.create_batch(database_session,batch)



    

class Batch(Base):
    __tablename__ = "batches"
    id : Mapped[int]= mapped_column(Integer, primary_key=True)
    # name : Mapped[str]= mapped_column(String)
    registration_id  : Mapped[int]  = mapped_column(Integer, ForeignKey(Registration.id))
    batch_no : Mapped[str]= mapped_column(String)
    manufactured_date  : Mapped[Date] =mapped_column(Date)
    expiry_date  : Mapped[Date] =mapped_column(Date)
    batch_size  : Mapped[int] =mapped_column(Integer)
    received_quantity  : Mapped[int] =mapped_column(Integer)
    created_at : Mapped[DateTime]  =mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at  : Mapped[DateTime] =  mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    registration = relationship("Registration", back_populates="batches")

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().all()
    
    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()
    
    @classmethod
    def create_batch(cls,db: AsyncSession,batch):
        db.add(batch)

    def update_batch(self, updated_data):
        for field, value in updated_data.items():
            setattr(self, field, value)


        
    
    
    


class Sample(Base):
    __tablename__ = "samples"
    id : Mapped[int]= mapped_column(Integer, primary_key=True)
    sample_id : Mapped[str]= mapped_column(String)
    name : Mapped[str]= mapped_column(String)
    batch_id : Mapped[int]  = mapped_column(Integer, ForeignKey(Batch.id))
    created_at : Mapped[DateTime]  =mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at  : Mapped[DateTime] =  mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    sample_requests = relationship("SampleRequest", back_populates="sample")
    sample_test_parameters = relationship("SampleTestParameter", back_populates="sample")


class SampleTestParameter(Base):
    __tablename__ = "sample_test_parameters"
    id : Mapped[int]= mapped_column(Integer, primary_key=True)
    sample_id : Mapped[int]  =  mapped_column(Integer, ForeignKey(Sample.id))
    test_parameter_id : Mapped[int] = mapped_column(Integer, ForeignKey(TestingParameter.id))
    test_type :Mapped[str] = mapped_column(Integer, ForeignKey(TestingParameter.id))
    created_at : Mapped[DateTime]  =mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at  : Mapped[DateTime] =  mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    sample = relationship("Sample", back_populates="sample_test_parameters")



class SampleStatus(Base):
    __tablename__ = "sample_status"
    id : Mapped[int]= mapped_column(Integer, primary_key=True)
    name : Mapped[str]= mapped_column(String)
    
class SampleRequest(Base):
    __tablename__ = "sample_requests"
    id : Mapped[int]= mapped_column(Integer, primary_key=True)
    sample_id : Mapped[int]  =  mapped_column(Integer, ForeignKey(Sample.id))
    sample_status_id : Mapped[int] = mapped_column(Integer, ForeignKey(SampleStatus.id))
    created_at : Mapped[DateTime]  =mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at  : Mapped[DateTime] =  mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    sample = relationship("Sample", back_populates="sample_requests")
    sample_request_history= relationship("SampleRequestHistory", back_populates="sample_request")


class SampleRequestHistory(Base):
    __tablename__ = "sample_requests_history"
    id : Mapped[int]= mapped_column(Integer, primary_key=True)
    sample_request_id : Mapped[int] = mapped_column(Integer, ForeignKey(SampleRequest.id))
    from_status_id : Mapped[int] = mapped_column(Integer, ForeignKey(SampleStatus.id))
    to_status_id : Mapped[int] = mapped_column(Integer, ForeignKey(SampleStatus.id))
    comments : Mapped[str] = mapped_column(String)
    created_at : Mapped[DateTime]  =mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    
    sample_request= relationship("SampleRequest", back_populates="sample_request_history")