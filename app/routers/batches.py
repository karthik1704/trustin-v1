from typing import Annotated, List, Optional
import datetime
from fastapi import APIRouter, Depends, Path, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.models.registrations import Batch

from app.database import get_async_db


from app.schemas.registrations import (
    BatchSchema,
    BatchCreate,
    BatchUpdate,
)

router = APIRouter(prefix="/batches", tags=["batches"])

db_dep = Annotated[AsyncSession, Depends(get_async_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


@router.get("/", response_model=Optional[list[BatchSchema]])
async def get_all_Batches(db_session: db_dep, current_user: user_dep):

    batches = await Batch.get_all(db_session, [])

    return batches


@router.get("/{batch_id}", response_model=BatchSchema)
async def get_sample(batch_id: int, db_session: db_dep, current_user: user_dep):
    batch = await Batch.get_one(db_session, [Batch.id == batch_id])
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


@router.post("/", response_model=BatchSchema)
async def create_batch(batch: BatchCreate, db_session: db_dep, current_user: user_dep):

    time = datetime.datetime.now()
    update_dict = {
        "created_at": time,
        "updated_at": time,
        "created_by": current_user["id"],
        "updated_by": current_user["id"],
    }
    batch_data = batch.model_dump()
    batch_data = {**batch_data, **update_dict}
    batch = Batch(**batch_data)
    db_session.add(batch)
    await db_session.commit()
    await db_session.refresh(batch)
    return batch


@router.put("/{batch_id}", response_model=BatchSchema)
async def update_batch(
    batch_id: int,
    updated_batch: BatchUpdate,
    db_session: db_dep,
    current_user: user_dep,
):

    batch_data = updated_batch.model_dump()

    batch = await Batch.get_one(db_session, [Batch.id == batch_id])
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    time = datetime.datetime.now()
    update_dict = {
        "updated_at": time,
        "updated_by": current_user["id"],
    }
    batch_data = {**batch_data, **update_dict}
    batch.update_batch(batch_data)

    await db_session.commit()
    await db_session.refresh(batch)

    return batch
