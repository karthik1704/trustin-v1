from typing import Annotated
from datetime import timedelta
from fastapi import Depends, Response, status, APIRouter, HTTPException
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from ..models.users import User
from ..schemas.users import Token
from ..utils import verify_password, create_access_token
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


class UserLogin(BaseModel):
    username: str
    password: str


db_dep = Annotated[AsyncSession, Depends(get_db)]


async def authenticate_user(email: str, password: str, db: db_dep) -> User | bool:
    user = await db.scalar(select(User).where(User.email==email))
    print(user)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


@router.post("/", response_model=Token)
async def login_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dep,
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )

    token = create_access_token(user.email, user.id, user.role, timedelta(minutes=30))
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=3600,
        secure=False,
        httponly=True,
        path="/",
        domain="localhost",
    )

    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", status_code=status.HTTP_201_CREATED)
async def get_token_for_user(user: UserLogin, db: db_dep):
    _user = authenticate_user(user.username, user.password, db)

    # TODO: out exception handling to external module
    if not _user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # TODO: add refresh token
    _token = create_access_token(
        _user.email, _user.id, _user.role, timedelta(minutes=30)
    )
    return {"access_token": _token, "token_type": "bearer"}


# @router.post("/logout", status_code=status.HTTP_201_CREATED, response_model=UserLogoutResponse)
# async def user_logout(user: UserLogout, request: Request, db_session: AsyncSession = Depends(get_db)):
#     _user: User = await User.find(db_session, [User.email == user.email])

#     # TODO: out exception handling to external module
#     if not _user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#     # TODO: remove access token
#     _token = await unset_jwt(request)
#     return {"message": "logged out"}
