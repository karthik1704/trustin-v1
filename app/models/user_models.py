from sqlalchemy import Column, Integer, String, ForeignKey
from app.models import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String )
    last_name = Column(String )
    email = Column(String, unique=True)
    password = Column(String)