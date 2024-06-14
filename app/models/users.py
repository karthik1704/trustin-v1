from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func, Enum
from sqlalchemy.orm import relationship
from app.models import Base
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select



class RoleType(str, PyEnum):
    QAHOD = 'QAHOD'
    MARKETING_ASST = 'MARKETING_ASST'
    MARKETING_HEAD = 'MARKETING_HEAD'
    ADMIN = 'ADMIN'
    MANAGEMENT = 'MANAGEMENT'
    ANALYST = 'ANALYST'
    FINANCETEAM = 'FINANCETEAM'



class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    sample_workflow_role = relationship("SampleWorkflow", back_populates="role",  lazy="selectin")

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars()
    

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String)    
    sample_workflow_department = relationship("SampleWorkflow", back_populates="department",  lazy="selectin")
    front_desks = relationship("FrontDesk",back_populates="department", uselist=True,   lazy="selectin")

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars()

class Menu(Base):
    __tablename__ = "menus"
    id = Column(Integer, primary_key=True)
    name = Column(String)


    

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

    phone = Column(String)

    date_joined = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean(), default=False)
    is_staff = Column(Boolean(), default=False)
    is_superuser = Column(Boolean(), default=False)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    qa_type_id = Column(Integer, ForeignKey("testtypes.id"), nullable=True)
    
    assingee = relationship("CustomerFollowUp", back_populates="marketing_user")
    followup_updated_user = relationship("CustomerFollowUpHistory", back_populates="user")
    # front_desks = relationship("FrontDesk", back_populates="user", foreign_keys=[FrontDesk.received_by])
    sample_assignee = relationship("Sample", foreign_keys="[Sample.assigned_to]", back_populates="assignee")
    sample_workflow_assignee = relationship("SampleWorkflow", foreign_keys="[SampleWorkflow.assigned_to]",   back_populates="assignee")
    sample_history_assignee = relationship("SampleHistory", foreign_keys="[SampleHistory.assigned_to]",   back_populates="assignee")
    sample_history_created = relationship("SampleHistory", foreign_keys="[SampleHistory.created_by]",   back_populates="created_by_user")
    # sample_created = relationship("Sample", foreign_keys="[Sample.created_by]", back_populates="created")

class MenuControlList(Base):
    __tablename__ = "menu_control_lists"
    id = Column(Integer, primary_key=True)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)


    
    @classmethod
    async def get_menus_for_role_and_department(
        cls, 
        database_session: AsyncSession, 
        role_id: int, 
        department_id: int
    ):
        
        where_conditions = []
        # if role_id:
        #     where_conditions.append(cls.role_id == role_id, )
        if department_id:
            # where_conditions.append(cls.department_id == department_id)
            where_conditions = [cls.department_id == department_id]
        
        print(where_conditions)
        if where_conditions:
            stmt = (
            select(Menu)
            # .select_from(Menu)
            .join(cls, Menu.id == cls.menu_id)
            .where(
                *where_conditions
            )
        )
        else:
            return []
        # print(stmt)

        result = await database_session.execute(stmt)
        s = result.scalars().all()
        print(s)
        return s
    