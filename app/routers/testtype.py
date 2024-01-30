from typing import Annotated
from fastapi import APIRouter, Depends, Path, status, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from ..schemas.samples import TestTypeCreate
from app.database import get_db
from ..models.samples import TestType

router = APIRouter(prefix="/testtypes", tags=["Test Type"])

db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_testtypes(db: db_dep, user: user_dep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    test_types = db.query(TestType).all()

    return test_types

@router.get("/trf", status_code=status.HTTP_200_OK)
async def get_all_testtypes_for_trf(db: db_dep):
    

    test_types = db.query(TestType).all()

    return test_types


@router.get('/{testtype_id}', status_code=status.HTTP_200_OK)
async def get_test_type(db:db_dep, user:user_dep, testtype_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    test_type = db.query(TestType).filter(TestType.id==testtype_id).first()

    return test_type

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_test_type(db: db_dep, data: TestTypeCreate, user: user_dep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    test_type = TestType(**data.model_dump())
    db.add(test_type)
    db.commit()

@router.put("/{testtype_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_test_type(
    db: db_dep,
    user: user_dep,
    data: TestTypeCreate,
    testtype_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    test_type = (
        db.query(TestType).filter(TestType.id == testtype_id).first()
    )

    if test_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test type Not Found"
        )

     

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(test_type, field, value)


    db.commit()
    db.refresh(test_type)