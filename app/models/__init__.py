from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


from .users import User
from .branches import Branch
from .customers import Customer, CustomerFollowUp, ContactPerson
from .samples import Product, TestType, TestingParameter
from .test_request_forms import TRF , TestingDetail
from .registrations import Registration