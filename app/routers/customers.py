from typing import Annotated
from fastapi import APIRouter, Depends, Path, status, HTTPException, Header
from sqlalchemy.orm import Session, joinedload

from app.dependencies.auth import get_current_user
from ..schemas.customers import CustomerCreate
from app.database import get_db
from ..models.customers import Customer, ContactPerson
router = APIRouter(
    prefix= '/customers',
    tags= ['Customers']
)

db_dep = Annotated[Session,Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]

@router.get('/', status_code=status.HTTP_200_OK)
async def get_all_Customers(db:db_dep, user : user_dep):
    # authorization: str = Header(...)
    print("sdsd")
    # print(Header.__dict__)
    # print()
    print(user)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    customers = db.query(Customer).all()

    return customers

@router.get('/{customer_id}', status_code=status.HTTP_200_OK)
async def get_Customer(db:db_dep, user:user_dep, customer_id:int = Path(gt=0)):
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    customer = db.query(Customer).options(joinedload(Customer.contact_persons)).filter(Customer.id==customer_id).first()

    return customer

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_Customers(db:db_dep, data:CustomerCreate,user:user_dep):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    contact_persons = data.contact_persons
    data_dict = data.model_dump()
    data_dict.pop("contact_persons")

    customer = Customer(**data_dict)
    db.add(customer)
    db.commit()
    db.refresh(customer)

    contacts = [
        ContactPerson(**contact.model_dump(), customer_id=customer.id) for contact in contact_persons
    ]
    db.add_all(contacts)
    db.commit()
    for contact in contacts:
        db.refresh(contact)
    db.refresh(customer)

    
    return {
        "customer":customer,
        "contacts": contacts 
    }
    