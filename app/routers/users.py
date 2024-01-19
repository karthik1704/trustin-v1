from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from ..schemas.users import UserCreate, ChangePassword, ForgotPassword
from app.database import get_db
from ..models.users import User
router = APIRouter(
    prefix= '/users',
    tags= ['Users']
)

db_dep = Annotated[Session,Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]

@router.get('/', status_code=status.HTTP_200_OK)
async def get_all_users(db:db_dep, user:user_dep):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    users = db.query(User).all()

    return users