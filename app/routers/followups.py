from typing import Annotated
from fastapi import APIRouter, Depends, Path, status, HTTPException, Header
from sqlalchemy.orm import Session, joinedload

from app.dependencies.auth import get_current_user
from ..schemas.customers import CustomerFollowupCreate
from app.database import get_db
from ..models.customers import CustomerFollowUp

router = APIRouter(prefix="/followups", tags=["Customers Followup"])

db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_customer_followups(db: db_dep, user: user_dep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    customers = (
        db.query(CustomerFollowUp)
        .options(joinedload(CustomerFollowUp.customer))
        .options(joinedload(CustomerFollowUp.marketing_user))
        .options(joinedload(CustomerFollowUp.product))
        .all()
    )

    return customers


@router.get("/{followup_id}", status_code=status.HTTP_200_OK)
async def get_Customer_followup(
    db: db_dep, user: user_dep, followup_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    customer = (
        db.query(CustomerFollowUp)
        .options(joinedload(CustomerFollowUp.customer))
        .options(joinedload(CustomerFollowUp.marketing_user))
        .options(joinedload(CustomerFollowUp.product))
        .filter(CustomerFollowUp.id == followup_id)
        .first()
    )

    return customer


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_followup(db: db_dep, data: CustomerFollowupCreate, user: user_dep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    data_dict = data.model_dump()

    followup = CustomerFollowUp(**data_dict)
    db.add(followup)
    db.commit()
    db.refresh(followup)


@router.put("/{followup_id}", status_code=status.HTTP_200_OK)
async def update_Customer_followup(
    db: db_dep,
    user: user_dep,
    data: CustomerFollowupCreate,
    followup_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    followup = (
        db.query(CustomerFollowUp).filter(CustomerFollowUp.id == followup_id).first()
    )

    if followup is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer Not Found"
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(followup, field, value)

    db.commit()
    db.refresh(followup)
