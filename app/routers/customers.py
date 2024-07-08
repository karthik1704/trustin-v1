from typing import Annotated
from fastapi import APIRouter, Depends, Path, status, HTTPException, Header
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.dependencies.auth import get_current_user
from app.utils import get_unique_code
from ..schemas.customers import CustomerCreate
from app.database import get_db
from ..models.customers import Customer, ContactPerson

router = APIRouter(prefix="/customers", tags=["Customers"])

db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_Customers_with_pagination(db: db_dep, user: user_dep,
                            page: int = 1, 
                            size: int = 10, 
                            search: Optional[str] = None, 
                            sort_by: str = "id", 
                            sort_order: str = "desc"):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    # customers = db.query(Customer).order_by(Customer.updated_at.desc()).all()
    query = db.query(Customer)
    if search:
        query = query.filter(Customer.company_name.ilike(f"%{search}%"))
    print(sort_by)
    print(sort_order)
    if sort_by and hasattr(Customer, sort_by):
        if sort_order == "asc":
            query = query.order_by(getattr(Customer, sort_by).asc())
        else:
            query = query.order_by(getattr(Customer, sort_by).desc())
    total_customers = query.count()
    customers = query.offset((page - 1) * size).limit(size).all()
    return {
        "data": customers,
        "total": total_customers,
        "page": page,
        "size": size
    }
@router.get("/all/", status_code=status.HTTP_200_OK)
async def get_all_Customers(db: db_dep, user: user_dep,):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    customers = db.query(Customer).order_by(Customer.updated_at.desc()).all()
   
    return customers

@router.get("/{customer_id}", status_code=status.HTTP_200_OK)
async def get_Customer(db: db_dep, user: user_dep, customer_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    customer = (
        db.query(Customer)
        .options(joinedload(Customer.contact_persons))
        .filter(Customer.id == customer_id)
        .first()
    )

    return customer


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_Customers(db: db_dep, data: CustomerCreate, user: user_dep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    contact_persons = data.contact_persons
    data_dict = data.model_dump()
    data_dict.pop("contact_persons")

    customer = Customer(**data_dict)
    db.add(customer)
    db.commit()
    db.refresh(customer)

    customer.customer_code = get_unique_code('CUS', customer.id) # type: ignore
    db.commit()

    contacts = [
        ContactPerson(**contact.model_dump(), customer_id=customer.id)
        for contact in contact_persons
    ]
    db.add_all(contacts)
    db.commit()
    for contact in contacts:
        db.refresh(contact)
    db.refresh(customer)

    return {"customer": customer, "contacts": contacts}


@router.put("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_customer(
    db: db_dep, user: user_dep, data: CustomerCreate, customer_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
    data_in_modified = data.copy(exclude={"contact_persons", })
    customer = (
        db.query(Customer)
        .options(joinedload(Customer.contact_persons))
        .filter(Customer.id == customer_id)
        .first()
    )


    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer Not Found"
        )

 

    for field, value in data_in_modified.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)

    # Update or add the children
    customer.contact_persons = [
        ContactPerson(**child.model_dump(), customer_id=customer_id)
        for child in data.contact_persons
    ]

    db.commit()
    db.refresh(customer)

    return customer
