from typing import Annotated
from fastapi import APIRouter, Depends, Path, status, HTTPException, Request
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.utils import get_hashed_password
from ..schemas.users import UserCreate, ChangePassword, ForgotPassword, UserUpdate, RoleSchema, DepartmentSchema
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.users import User
from app.utils import get_hashed_password
from app.models import Role, Department

router = APIRouter(prefix="/roles", tags=["Roles"])
from app.database import get_db, get_async_db

# db_dep = Annotated[Session, Depends(get_db)]
# user_dep = Annotated[dict, Depends(get_current_user)]



# GET method to retrieve all the roles
@router.get("/", response_model=list[RoleSchema])
async def get_roles(request: Request,db_session: AsyncSession = Depends(get_async_db),  current_user: dict = Depends(get_current_user)):
    print("coming -----")
    roles = await Role.get_all(db_session,[])
    return roles

