from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Path, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.auth import get_current_user
from app.database import get_db, get_async_db
from app.models.front_desks import FrontDesk
from app.schemas.front_desks import FrontDeskCreate, FrontDeskSchema, FrontDeskUpdate


router = APIRouter(prefix="/front-desks", tags=["front-desk"])

db_dep = Annotated[AsyncSession, Depends(get_async_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


@router.get("/", response_model=list[FrontDeskSchema])
async def get_all_front_desks(
    request: Request, db_session: db_dep, current_user: user_dep
):

    try:
        _data = await FrontDesk.get_all(db_session, [])
        return _data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/under-registrations", response_model=list[FrontDeskSchema])
async def get_all_front_desk_by_under_registration(db_session: db_dep, current_user: user_dep):
    try:
        _data = await FrontDesk.get_all(db_session, [FrontDesk.status == "UNDER_REGISTRATION"])
        return _data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{id}", response_model=Optional[FrontDeskSchema])
async def get_front_desk(id: int, db_session: db_dep, current_user: user_dep):
    try:
        _data = await FrontDesk.get_one(db_session, [FrontDesk.id == id])
        return _data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_front_desk(
    data: FrontDeskCreate, db_session: db_dep, current_user: user_dep
):
    update_dict = {
        "created_by": current_user["id"],
        "updated_by": current_user["id"],
        "received_by": current_user["id"],
    }
    _data = data.model_dump()
    front_desk_data = {**_data, **update_dict}

    desk_data = FrontDesk(**front_desk_data)
    db_session.add(desk_data)
    await db_session.commit()
    await db_session.refresh(desk_data)

    return desk_data


@router.put("/{id}", response_model=FrontDeskSchema)
async def update_front_desk(
    id: int, data: FrontDeskUpdate, db_session: db_dep, current_user: user_dep
):
    _data = data.model_dump()

    front_desk = await FrontDesk.get_one(db_session, [FrontDesk.id == id])
    if front_desk is None:
        raise HTTPException(status_code=404, detail="Data not found")
    update_dict = {
        "updated_by": current_user["id"],
    }
    update_data = {**_data, **update_dict}
    front_desk.update_front_desk(update_data)

    await db_session.commit()
    await db_session.refresh(front_desk)

    return front_desk

@router.delete("/{id}")
async def delete_front_desk(
    id: int, db_session: db_dep, current_user: user_dep
):
    
    front_desk = await FrontDesk.get_one(db_session, [FrontDesk.id == id])
    if front_desk is None:
        raise HTTPException(status_code=404, detail="Data not found")
   
    await db_session.delete(front_desk)
    await db_session.commit()
    
