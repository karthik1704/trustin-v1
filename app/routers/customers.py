from typing import Annotated
from fastapi import APIRouter, Depends, Path, status, HTTPException, Header
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.dependencies.auth import get_current_user
from app.utils import get_unique_code
from ..schemas.customers import CustomerCreate, CustomerListSchema, CustomerUpdate
from app.database import get_db
from ..models.customers import Customer, ContactPerson

router = APIRouter(prefix="/customers", tags=["Customers"])

db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_Customers_with_pagination(
    db: db_dep,
    user: user_dep,
    page: int = 1,
    size: int = 10,
    search: Optional[str] = None,
    sort_by: str = "id",
    sort_order: str = "desc",
):
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
    return {"data": customers, "total": total_customers, "page": page, "size": size}


@router.get("/all/", status_code=status.HTTP_200_OK)
async def get_all_Customers(
    db: db_dep,
    user: user_dep,
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    customers = (
        db.query(Customer)
        .options(joinedload(Customer.contact_persons))
        .order_by(Customer.updated_at.desc())
        .all()
    )

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

    customer.customer_code = get_unique_code("CUS", customer.id)  # type: ignore
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
    db: db_dep, user: user_dep, data: CustomerUpdate, customer_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
   # Find the customer
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

    # Update customer fields except for contact persons
    data_in_modified = data.model_dump(exclude={"contact_persons"})
    for field, value in data_in_modified.items():
        setattr(customer, field, value)

    # Update existing contact persons
    existing_contact_person_ids = {cp.id for cp in customer.contact_persons if cp.id is not None}
    updated_contact_person_ids = {cp.id for cp in data.contact_persons if cp.id is not None}

    # Create a mapping of existing contact persons by ID for quick lookup
    contact_person_map = {cp.id: cp for cp in customer.contact_persons if cp.id is not None}

    for contact_person_data in data.contact_persons:
        if contact_person_data.id:  # If ID is provided, update the existing contact person
            if contact_person_data.id in contact_person_map:
                contact_person = contact_person_map[contact_person_data.id]
                for field, value in contact_person_data.model_dump(exclude_unset=True).items():
                    setattr(contact_person, field, value)
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Contact Person with ID {contact_person_data.id} not found"
                )
        else:  # If no ID is provided, add as a new contact person
            new_contact_person = ContactPerson(**contact_person_data.dict(), customer_id=customer_id)
            db.add(new_contact_person)

    # Remove contact persons that are no longer in the updated list
    customer.contact_persons = [
        cp for cp in customer.contact_persons if cp.id in updated_contact_person_ids
    ]

    db.commit()
    db.refresh(customer)