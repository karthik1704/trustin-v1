import os
from datetime import datetime, timedelta, UTC
from typing import Union, Any, Optional
from jose import jwt
from passlib.context import CryptContext
from fiscalyear import FiscalYear, setup_fiscal_calendar

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = "248BA6C7F1468"  # should be kept secret
JWT_REFRESH_SECRET_KEY = "test"


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def create_access_token(username: str,
    email: str, user_id: int, role_id: int,department_id:Optional[int], expires_delta: int|None = None
) -> str:
    if expires_delta is not None:
        expires_at = datetime.now(UTC) + timedelta(days=30)
    else:
        expires_at = datetime.now(UTC) + timedelta(days=30)

    print(expires_at)

    encode = {"sub": email, "id": user_id, "role_id": role_id, "dept_id" : department_id}
    encode.update({"exp": expires_at})
    encoded_jwt = jwt.encode(encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    email: str, user_id: int, role: str, expires_delta: int | None = None
) -> str:
    if expires_delta is not None:
        expires_at = datetime.now(UTC) + timedelta(days=expires_delta)

    else:
        expires_at = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_MINUTES)
    encode = {"sub": email, "id": user_id, "role": role}
    encode.update({"exp": expires_at})
    encoded_jwt = jwt.encode(encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])


def get_unique_code(prefix: str, unique_number: int) -> str:
    setup_fiscal_calendar(start_month=4)
    start_year = FiscalYear.current().start.strftime("%Y")[-2:]
    end_year = FiscalYear.current().end.strftime("%Y")[-2:]
    pre=prefix+"/" if prefix else ""
    new_code = f"TAS/{pre}{start_year}-{end_year}/{unique_number:04}" 

    return new_code

start_number:int|None = None

def get_unique_code_registration(unique_number: int, code:str) -> str:
    setup_fiscal_calendar(start_month=4)
   
    start_year = FiscalYear.current().start.strftime("%Y")[-2:]
    end_year = FiscalYear.current().end.strftime("%Y")[-2:]
    if code is not None:
        code_years = code.split('/')[1]
        code_end_year = code_years.split('-')[1]
        if code_end_year == start_year:
            unique_number=1
    if start_number is not None:
        unique_number=start_number
    new_code = f"TAS/{start_year}-{end_year}/{unique_number:04}" 

    print( new_code)
    return new_code

if __name__== "__main__":
    get_unique_code_registration (10, 'TAS/24-25/0009')
    get_unique_code_registration( 1, 'TAS/23-24/0009')