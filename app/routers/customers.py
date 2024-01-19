from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

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
async def get_all_Customers(db:db_dep, user:user_dep):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    customers = db.query(Customer).all()

    return customers

@router.post('/', status_code=status.HTTP_200_OK)
async def create_Customers(db:db_dep, data:CustomerCreate,user:user_dep):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    customer = customer(**data.model_dump())
    db.add(customer)
    db.commit()
    

    