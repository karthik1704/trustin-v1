from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..schemas.users import UserCreate, ChangePassword, ForgotPassword
from app.database import get_db
from ..models.users import User
router = APIRouter(
    prefix= '/users',
    tags= ['Users']
)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_all_users(db:Session=Depends(get_db)):
    users = db.query(User).all()

    return users