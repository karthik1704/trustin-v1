from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from app.models import Base

if TYPE_CHECKING:
    from .samples import Product, TestingParameter
    from .test_request_forms import TRF

class Branch(Base):
    __tablename__ = "branches"

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    branch_name: Mapped[str] = mapped_column(unique=True, index=True)
    address_line1:Mapped[str]
    address_line2:Mapped[str]
    mobile_number:Mapped[str]
    landline_number:Mapped[str]
    email:Mapped[str]
    pan_no:Mapped[str]
    cin:Mapped[str]
    gstin:Mapped[str]
    bank_details:Mapped[str]
    ifsc_code:Mapped[str]

    # products = relationship('Product', back_populates='branch')
    # parameters = relationship('TestingParameter',back_populates="branch" )
    # trfs = relationship('TRF', back_populates='branch')

    products: Mapped[List["Product"]] = relationship(back_populates="branch")
    parameters: Mapped[List["TestingParameter"]] = relationship(back_populates="branch")
    trfs: Mapped[List["TRF"]] = relationship(back_populates="branch")

