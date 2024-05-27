from typing import Annotated
from fastapi import APIRouter, Depends, Path, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from ..schemas.branches import Branch as BranchCreate, BranchSchema
from app.database import get_async_db
from ..models.branches import Branch

router = APIRouter(prefix="/branch", tags=["Branches"])

db_dep = Annotated[AsyncSession, Depends(get_async_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK, response_model=BranchSchema)
async def get_all_branches(db: db_dep, user: user_dep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    branches = await Branch.get_all(db, [])

    return branches


@router.get("/{branch_id}", status_code=status.HTTP_200_OK)
async def get_branch(db: db_dep, user: user_dep, branch_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    branch = Branch.get_one(db, [Branch.id == branch_id])

    return branch


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_branch(data: BranchCreate, db: db_dep, user: user_dep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
    branch_data = data.model_dump()

    already_exists = await Branch.get_one(
        db, [Branch.branch_name == branch_data.get("branch_name")]
    )
    if already_exists is not None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Branch name already exists.",
        )
    branch = Branch(**branch_data)
    db.add(branch)
    await db.commit()


@router.put("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_branch(
    db: db_dep,
    user: user_dep,
    data: BranchCreate,
    branch_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    branch = await Branch.get_one(db, [Branch.id == branch_id])

    if branch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Branch Not Found"
        )

    branch_data = data.model_dump()

    branch.update_branch(**branch_data)
    await db.commit()
