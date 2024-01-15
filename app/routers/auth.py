from fastapi import APIRouter, status

from schemas.users import UserCreate, ChangePassword, ForgotPassword


router = APIRouter(
    prefix= '/auth',
    tags= ['Auth']
)