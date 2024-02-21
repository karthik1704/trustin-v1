from typing import Annotated, List
from fastapi import APIRouter, Depends, Path, Query, status, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.dependencies.auth import get_current_user
from app.models.samples import TestType, TestingParameter
from ..schemas.test_request_form import TRFCreate
from app.database import get_db
from ..models.test_request_forms import TRF, TestingDetail

router = APIRouter(prefix="/trf", tags=["Test Requst Forms"])

db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_trf(db: db_dep, user: user_dep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    customers = (
        db.query(TRF)
        .options(joinedload(TRF.test_details))
        .options(joinedload(TRF.customer))
        .options(joinedload(TRF.product))
        .options(joinedload(TRF.followup))
        .options(joinedload(TRF.test_types))
        .options(joinedload(TRF.test_details))
        .all()
    )

    return customers


@router.get("/customer/{trf_id}", status_code=status.HTTP_200_OK)
async def get_trf_customer(db: db_dep, trf_id: str):
    trf = (
        db.query(TRF)
        .options(joinedload(TRF.test_details))
        .options(joinedload(TRF.customer))
        .options(joinedload(TRF.product))
        .options(joinedload(TRF.followup))
        .options(joinedload(TRF.test_types))
        .options(joinedload(TRF.test_details))
        .filter(TRF.trf_code == trf_id)
        .first()
    )

    return trf


# @router.get("/test-details/{trf_code}", status_code=status.HTTP_200_OK)
# async def get_test_details(
#     db: db_dep,
#     user: user_dep,
#     trf_code: str,
#     test_type: List[int] = Query(..., description="List of test_type IDs"),
# ):
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
#         )
    
#     trf = db.query(TRF).filter(TRF.trf_code==trf_code).first()

#     if trf is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="TRF not found"
#         )
    
#     test_details = (
#         db.query(TestingParameter)
#         .filter(TestingParameter.product_id == trf.product_id)
#         .filter(TestingParameter.test_type_id.in_(test_type))
#         .options(joinedload(TestingParameter.branch))
#         .options(joinedload(TestingParameter.test_type))
#         .options(joinedload(TestingParameter.product))
#         .all()
#     )

#     return test_details


@router.get("/{trf_id}", status_code=status.HTTP_200_OK)
async def get_trf(db: db_dep, user: user_dep, trf_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    trf = (
        db.query(TRF)
        .options(
            joinedload(TRF.test_details)
            .joinedload(TestingDetail.parameter)
            .joinedload(TestingParameter.test_type)
        )
        .order_by(TestingDetail.priority_order)
        .options(joinedload(TRF.customer))
        .options(joinedload(TRF.product))
        .options(joinedload(TRF.followup))
        .options(joinedload(TRF.test_types))
        .filter(TRF.id == trf_id)
        .first()
    )
    if trf is not None:
        trf_dict = trf.__dict__
        trf_dict["test_types_ids"] = [item.id for item in trf.test_types]

    return trf_dict


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_trf(db: db_dep, data: TRFCreate, user: user_dep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    test_details = data.test_details
    test_type_ids = data.test_types_ids
    data_dict = data.model_dump()
    data_dict.pop("test_details")
    data_dict.pop("test_types_ids")

    trf = TRF(**data_dict)
    db.add(trf)
    db.commit()
    db.refresh(trf)

    for test_type_id in test_type_ids:
        test_type = db.query(TestType).get(test_type_id)
        if test_type:
            trf.test_types.append(test_type)
        else:
            raise HTTPException(
                status_code=404, detail=f"Category with ID {test_type_id} not found"
            )

    db.commit()
    db.refresh(trf)

    tests = [TestingDetail(**test.model_dump(), trf_id=trf.id) for test in test_details]
    db.add_all(tests)
    db.commit()
    for test in tests:
        db.refresh(test)
    db.refresh(trf)

    return {"trf": trf, "test_details": tests}


@router.put("/admin/{trf_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_trf_admin(db: db_dep, data: TRFCreate, user: user_dep, trf_id: int):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    data_in_modified = data.copy(exclude={"testing_details", "test_types_ids"})

    trf = (
        db.query(TRF)
        .options(joinedload(TRF.test_details))
        .filter(TRF.id == trf_id)
        .first()
    )

    if trf is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="TRF Not Found"
        )

    for key, value in data_in_modified.model_dump(exclude_unset=True).items():
        setattr(trf, key, value)
    # Update test types relationships
    trf.test_types = []
    for test_type_data in data.test_types_ids:
        test_type = db.query(TestType).get(test_type_data)
        if test_type:
            trf.test_types.append(test_type)

    # Update testing details relationships
    trf.test_details = [
        TestingDetail(**detail.model_dump(), trf_id=trf.id)
        for detail in data.testing_details
    ]

    # Commit changes
    db.commit()
    db.refresh(trf)


@router.put("/{trf_code}", status_code=status.HTTP_204_NO_CONTENT)
async def update_trf(db: db_dep, data: TRFCreate, trf_code: str):
    data_in_modified = data.copy(exclude={"testing_details", "test_types_ids"})

    trf = (
        db.query(TRF)
        .options(joinedload(TRF.test_details))
        .filter(TRF.trf_code == trf_code)
        .first()
    )

    if trf is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="TRF Not Found"
        )

    for key, value in data_in_modified.model_dump(exclude_unset=True).items():
        setattr(trf, key, value)
    # Update test types relationships
    trf.test_types = []
    for test_type_data in data.test_types_ids:
        test_type = db.query(TestType).get(test_type_data)
        if test_type:
            trf.test_types.append(test_type)

    # Update testing details relationships
    trf.test_details = [
        TestingDetail(**detail.model_dump(), trf_id=trf.id)
        for detail in data.testing_details
    ]

    # Commit changes
    db.commit()
    db.refresh(trf)
