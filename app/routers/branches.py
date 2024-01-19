from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from ..schemas.branches import  Branch as BranchCreate
from app.database import get_db
from ..models.branches import Branch
router = APIRouter(
    prefix= '/branch',
    tags= ['Branches']
)

db_dep = Annotated[Session,Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]

@router.get('/', status_code=status.HTTP_200_OK)
async def get_all_branches(db:db_dep, user:user_dep):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    customers = db.query(Branch).all()

    return customers

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_branch(db:db_dep, data:BranchCreate,user:user_dep):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    # already_exists = db.query(Branch).filter(Branch.branch_name.() == data.branch_name.casefold()).first()

    # if already_exists is not None:
    #     raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f'{data.branch_name} is already exists.')
    
    branch = Branch(**data.model_dump())
    db.add(branch)
    db.commit()
    

    