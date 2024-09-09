from datetime import datetime
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Path, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.auth import get_current_user
from app.database import  get_async_db
from app.models.quotations import Quotation, QuotationWorkflow

from app.schemas.quotations import QuotationCreate, QuotationSchema, QuotationUpdate


router = APIRouter(prefix="/quotations", tags=["Quotations"])

db_dep = Annotated[AsyncSession, Depends(get_async_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


@router.get("/", response_model=dict)
async def get_quotations_paginated(
    request: Request,
    db_session: db_dep,
    current_user: user_dep,
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None
):
    try:
        result = await Quotation.get_all_pagination(
            db_session,
            where_conditions=[],
            page=page,
            page_size=page_size,
            search=search
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/all", response_model=list[QuotationSchema])
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
        raise HTTPException(status_code=404, detail="Quotation not found")

    update_dict = {
        "updated_by": current_user["id"],
    }
    update_data = {**_data, **update_dict}
    await quotation.update_quotation(update_data)

    await db_session.commit()
    await db_session.refresh(quotation)

    return quotation


@router.patch("/{quotation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def patch_quotation(
    quotation_id: int,
    updated_quotation: QuotationUpdate,
    db_session: AsyncSession = Depends(get_async_db),
    current_user: dict = Depends(get_current_user),
):
    quotation_data = updated_quotation.model_dump(exclude_unset=True)

    quotation = await Quotation.get_one(db_session, [Quotation.id == quotation_id])
    if quotation is None:
        raise HTTPException(status_code=404, detail="Quotation not found")

    time = datetime.now()
    update_dict = {
        "updated_at": time,
        "updated_by": current_user["id"],
    }
    comments = quotation_data.pop("comments", "")

    extra_data: dict[str, str] = {}

    quotation_data = {**quotation_data, **update_dict, **extra_data}

    prev_status = quotation.status
    if quotation_data.get("status", "") == "Submitted" and prev_status != "Submitted":
        await quotation.update_quotation(quotation_data)

        await quotation.create_workflow(db_session, current_user)
        history = {
            "quotation_id": quotation_id,
            "created_at": time,
            "created_by": current_user["id"],
            "from_status_id": 1,
            "to_status_id": 2,
        }
        if quotation_data.get("assigned_to", ""):
            history.update({"assigned_to": quotation_data.get("assigned_to", "")})
        if comments:
            history.update({"comments": comments})

        await quotation.create_history(db_session, current_user, history)
    else:
        if quotation_data.get("status_id", ""):
            if "status_id" in quotation_data:
                status_id = quotation_data.pop("status_id", "")

            await quotation.update_quotation(quotation_data)
            quotation_data.update({"status_id": status_id})
            progress = await QuotationWorkflow.get_one(
                db_session,
                [
                    QuotationWorkflow.quotation_id == quotation_id,
                    QuotationWorkflow.status == "In Progress",
                ],
            )

            progress_status_id = progress.quotation_status_id if progress else 0
            if progress and quotation_data.get("status_id", "") == progress_status_id + 1:
                # moving forward
                update_dict = {
                    "status": "Done",
                    "updated_at": time,
                    "updated_by": current_user["id"],
                }
                if quotation_data.get("assigned_to", ""):
                    update_dict.update(
                        {"assigned_to": quotation_data.get("assigned_to", "")}
                    )


@router.delete("/{id}")
async def delete_quotation(id: int, db_session: db_dep, current_user: user_dep):
    quotation = await Quotation.get_one(db_session, [Quotation.id == id])
    if quotation is None:
        raise HTTPException(status_code=404, detail="Quotation not found")

    await db_session.delete(quotation)
    await db_session.commit()
