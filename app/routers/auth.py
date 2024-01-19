from typing import Annotated
from datetime import timedelta
from fastapi import Depends, status, APIRouter, HTTPException
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from ..models.users import User
from ..schemas.users import Token
from ..utils import  verify_password, create_access_token
from ..database import get_db
router = APIRouter(
    prefix='/auth',
    tags = ['auth']
)










db_dep = Annotated[Session, Depends(get_db)]


def  authenticate_user(email:str, password:str, db):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


@router.post('/', response_model=Token)
async def login_access_token(form_data:Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dep):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

    token = create_access_token(user.email, user.id, user.role,timedelta(minutes=30))
    return {'access_token': token, 'token_type':'bearer'}