from typing import Annotated
from fastapi import APIRouter, Depends, Path, status, HTTPException, Header
from sqlalchemy.orm import Session, joinedload

from app.dependencies.auth import get_current_user
from app.models.test_request_forms import TRF
from app.utils import get_unique_code
from ..schemas.customers import CustomerFollowupCreate
from app.database import get_db
from ..models.customers import CustomerFollowUp, MarketingStatus, CustomerFollowUpHistory

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
        .options(joinedload(CustomerFollowUp.trf))
        .order_by(CustomerFollowUp.id.desc())
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
        .options(joinedload(CustomerFollowUp.trf))
         .options(joinedload(CustomerFollowUp.customer_followup_history))
         .options(joinedload(CustomerFollowUp.customer_followup_history, CustomerFollowUpHistory.user))
        #  .options(joinedload(CustomerFollowUp.customer_followup_history.user))
        #  .options(joinedload(CustomerFollowUpHistory.user))
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
    # followup = followup.dict()
    history_dict = {
        "customer_followup_id" : followup.id,
        "marketing_status" : followup.marketing_status.name,
        "user_id" : user["id"],
        "date" : followup.date,
        "remarks" : followup.remarks
    }
    print(history_dict)
    history = CustomerFollowUpHistory(**history_dict)
    db.add(history)
    db.commit()
    db.refresh(history)


@router.put("/{followup_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_customer_followup(
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
    history_dict = {
        "customer_followup_id" : followup.id,
        "marketing_status" : followup.marketing_status,
        "user_id" : user["id"],
        "date" : followup.date,
        "remarks" : followup.remarks
    }
    history = CustomerFollowUpHistory(**history_dict)
    db.add(history)
    db.commit()
    db.refresh(history)

    if followup.marketing_status == MarketingStatus.WON: # type: ignore

        trf = TRF(product_id=followup.product_id, customer_id=followup.customer_id, )
        followup.trf=trf
        db.commit()
        db.refresh(followup)
        db.refresh(trf)

        trf.trf_code = get_unique_code('TRF', trf.id)
        db.commit()
        


        