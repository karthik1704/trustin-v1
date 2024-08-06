from typing import Annotated, List
from fastapi import APIRouter, Depends, Path, Query, status, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.dependencies.auth import get_current_user
from app.utils import get_unique_code, get_unique_para_code
from ..schemas.samples import TestParameterCreate
from app.database import get_db
from ..models.samples import TestingParameter

router = APIRouter(prefix="/parameters", tags=["Testing Parameters"])

db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_testing_parameters(db: db_dep, user: user_dep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    parameters = (
        db.query(TestingParameter)
        .options(joinedload(TestingParameter.branch))
        .options(joinedload(TestingParameter.test_type))
        .options(joinedload(TestingParameter.product))
        .all()
    )

    return parameters


@router.get("/product/{product_id}", status_code=status.HTTP_200_OK)
async def get_all_testing_parameters_by_product_id(
    db: db_dep,
    user: user_dep,
    test_type: List[int] = Query(..., description="List of test_type IDs"),
    product_id: int = Path(gt=0),
):
    parameters = (
        db.query(TestingParameter)
        .filter(TestingParameter.product_id == product_id)
        .filter(TestingParameter.test_type_id.in_(test_type))
        .options(joinedload(TestingParameter.branch))
        .options(joinedload(TestingParameter.test_type))
        .options(joinedload(TestingParameter.product))
        .all()
    )

    return parameters


@router.get("/{para_id}", status_code=status.HTTP_200_OK)
async def get_test_type(db: db_dep, user: user_dep, para_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    parameter = (
        db.query(TestingParameter).filter(TestingParameter.id == para_id).first()
    )

    return parameter


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_parameter(db: db_dep, data: TestParameterCreate, user: user_dep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    parameter_data = data.model_dump()
    test_type_id = parameter_data.pop("test_type_id")
    product_id = parameter_data.pop("product_id", None)
    methods = parameter_data.pop("methods", [])

    # Check if methods are provided
    if not methods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No methods provided"
        )

    # Collecting all parameters in a single loop
    parameters_to_add = []
    for method in methods:
        method_or_spec = method.pop("method_or_spec")
        parameters = method.pop("parameters", [])
        if not parameters:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No Parameters provided"
            )
        for param in parameters:
            param_data = {
                **param,
                "test_type_id": test_type_id,
                "product_id": product_id,
                "method_or_spec": method_or_spec,
                "parameter_code": None,  # Ensure this is handled later if needed
            }
            parameter = TestingParameter(**param_data)
            parameters_to_add.append(parameter)

    # Adding all parameters at once
    db.add_all(parameters_to_add)
    db.commit()


@router.put("/{para_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_test_parameter(
    db: db_dep,
    user: user_dep,
    data: TestParameterCreate,
    para_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    parameter = (
        db.query(TestingParameter).filter(TestingParameter.id == para_id).first()
    )

    if parameter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Testing Parameter Not Found"
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(parameter, field, value)

    db.commit()
    db.refresh(parameter)
