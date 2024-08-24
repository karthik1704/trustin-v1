from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Path, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.auth import get_current_user
from app.database import  get_async_db
from app.models.quotations import Quotation

from app.schemas.quotations import QuotationCreate, QuotationSchema, QuotationUpdate


router = APIRouter(prefix="/quotations", tags=["Quotations"])

db_dep = Annotated[AsyncSession, Depends(get_async_db)]
user_dep = Annotated[dict, Depends(get_current_user)]





@router.get("/", response_model=list[QuotationSchema])
async def get_all_quotations(
    request: Request, db_session: db_dep, current_user: user_dep
):

    try:
        _data = await Quotation.get_all(db_session, [])
        return _data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/{id}", response_model=Optional[QuotationSchema])
async def get_quotations(id: int, db_session: db_dep, current_user: user_dep):
    try:
        _data = await Quotation.get_one(db_session, [Quotation.id == id])
        return _data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_quotation(
    data: QuotationCreate, db_session: db_dep, current_user: user_dep
):
    update_dict = {
        "created_by": current_user["id"],
        "updated_by": current_user["id"],
        "received_by": current_user["id"],
    }
    _data = data.model_dump()
    quotation_data = {**_data, **update_dict}

    q_data = Quotation(**quotation_data)
    db_session.add(q_data)
    await db_session.commit()
    await db_session.refresh(q_data)

    return q_data


@router.put("/{id}", response_model=QuotationSchema)
async def update_quotation(
    id: int, data: QuotationUpdate, db_session: db_dep, current_user: user_dep
):
    _data = data.model_dump()

    quotation = await Quotation.get_one(db_session, [Quotation.id == id])
    if quotation is None:
        raise HTTPException(status_code=404, detail="Data not found")
    update_dict = {
        "updated_by": current_user["id"],
    }
    update_data = {**_data, **update_dict}
    quotation.update_front_desk(update_data)

    await db_session.commit()
    await db_session.refresh(quotation)

    return quotation


@router.delete("/{id}")
async def delete_quotation(id: int, db_session: db_dep, current_user: user_dep):

    quotation = await Quotation.get_one(db_session, [Quotation.id == id])
    if quotation is None:
        raise HTTPException(status_code=404, detail="Data not found")

    await db_session.delete(quotation)
    await db_session.commit()
