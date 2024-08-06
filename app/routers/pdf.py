from typing import Annotated, List, Optional
import datetime
from fastapi import APIRouter, Depends, Path, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.models.registrations import Batch, Sample

from app.database import get_async_db
from app.schemas.registrations import SampleSchema




router = APIRouter(prefix="/pdf", tags=["Pdf"])

db_dep = Annotated[AsyncSession, Depends(get_async_db)]
user_dep = Annotated[dict, Depends(get_current_user)]





@router.get("/{sample_id}", response_model=SampleSchema)
async def get_sample(
    sample_id: int,
    db_session: AsyncSession = Depends(get_async_db),
):
    sample = await Sample.get_one(db_session, [Sample.id == sample_id])
    if sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample


