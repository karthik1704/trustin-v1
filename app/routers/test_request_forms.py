from typing import Annotated
from fastapi import APIRouter, Depends, Path, status, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.dependencies.auth import get_current_user
from app.models.samples import TestType
from ..schemas.test_request_form import TRFCreate
from app.database import get_db
from ..models.test_request_forms import TRF, TestingDetail
router = APIRouter(
    prefix= '/trf',
    tags= ['Test Requst Forms']
)

db_dep = Annotated[Session,Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]

@router.get('/', status_code=status.HTTP_200_OK)
async def get_all_trf(db:db_dep, user:user_dep):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    customers = db.query(TRF).all()

    return customers

@router.get('/{trf_id}', status_code=status.HTTP_200_OK)
async def get_trf(db:db_dep, user:user_dep, trf_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    customer = db.query(TRF).options(joinedload(TRF.test_details)).filter(TRF.id==trf_id).first()

    return customer

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_trf(db:db_dep, data:TRFCreate,user:user_dep):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
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
            raise HTTPException(status_code=404, detail=f"Category with ID {test_type_id} not found")

    db.commit()
    db.refresh(trf)

    tests = [
        TestingDetail(**test.model_dump(), trf_id=trf.id) for test in test_details
    ]
    db.add_all(tests)
    db.commit()
    for test in tests:
        db.refresh(test)
    db.refresh(trf)

    
    return {
        "trf":trf,
        "test_details": tests 
    }
    