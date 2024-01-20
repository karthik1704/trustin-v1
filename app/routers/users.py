from typing import Annotated
from fastapi import APIRouter, Depends, Path, status, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.utils import get_hashed_password
from ..schemas.users import UserCreate, ChangePassword, ForgotPassword
from app.database import get_db
from ..models.users import User
from app.utils import get_hashed_password
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

@router.get('/{user_id}', status_code=status.HTTP_200_OK)
async def get_user(db:db_dep, user:user_dep, user_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    user = db.query(User).filter(User.id==user_id).first()

    return user

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dep, user:user_dep, data:UserCreate):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    plain_password = data.password
    plain_password2 = data.password2
    user_dict = data.model_dump()
    user_dict.pop('password')
    user_dict.pop('password2')

    if plain_password != plain_password2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Password Does not match")

    user_exists = db.query(User).filter(User.email==user_dict.get('email')).first()

    if user_exists is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User already Exists")


    user = User(**user_dict, password=get_hashed_password(plain_password) )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user