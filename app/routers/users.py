from typing import Annotated, List
from fastapi import APIRouter, Depends, Path, status, HTTPException, Request
from sqlalchemy.orm import Session, joinedload

from app.dependencies.auth import get_current_user
from app.utils import get_hashed_password, verify_password
from ..schemas.users import (
    UserCreate,
    ChangePassword,
    ForgotPassword,
    UserListSchema,
    UserSchema,
    UserUpdate,
    RoleSchema,
    DepartmentSchema,
)
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.users import MenuControlList, User
from app.utils import get_hashed_password
from app.models import Role, Department

router = APIRouter(prefix="/users", tags=["Users"])
from app.database import get_db, get_async_db

db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[UserListSchema])
async def get_all_users(db: db_dep, user: user_dep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    users = (
        db.query(User)
        .options(joinedload(User.department))
        .options(joinedload(User.role))
        .all()
    )

    return users


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_loggedin_user(db: db_dep, user: user_dep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
    print(user)
    users = db.query(User).filter(User.id == user["id"]).first()

    return users


@router.get("/menus", status_code=status.HTTP_200_OK)
async def get_menus(
    db_session: AsyncSession = Depends(get_async_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
    print(current_user)
    role_id = current_user.get("role_id", 0)
    department_id = current_user.get("dept_id", 0)
    print("sss")
    menus = await MenuControlList.get_menus_for_role_and_department(
        db_session, role_id, department_id
    )

    return menus


@router.get("/departments/{deparment_id}", status_code=status.HTTP_200_OK)
async def get_all_user_by_department(db: db_dep, user: user_dep, deparment_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    users = db.query(User).filter(User.department_id == deparment_id).all()

    return users

@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(db: db_dep, user: user_dep, user_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    user_data = db.query(User).filter(User.id == user_id).first()

    return user_data


@router.get("/role/{role}", status_code=status.HTTP_200_OK)
async def get_all_users_by_role(db: db_dep, user: user_dep, role_id: int):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    users = db.query(User).filter(User.role_id == role_id).all()

    return users


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dep, user: user_dep, data: UserCreate):
    print(data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
    plain_password = data.password
    plain_password2 = data.password2
    user_dict = data.model_dump()
    user_dict.pop("password")
    user_dict.pop("password2")

    if plain_password != plain_password2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Password Does not match"
        )

    user_username_exists = (
        db.query(User).filter(User.username == user_dict.get("username")).first()
    )

    if user_dict.get("email"):
        user_email_exists = (
            db.query(User).filter(User.email == user_dict.get("email")).first()
        )
        if user_email_exists is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User already exists with this email",
            )
    if user_username_exists is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Username not avaiable, Try another username",
        )
    is_superuser = False
    if user_dict.get("role") == 1:
        is_superuser = True

    user = User(
        **user_dict,
        password=get_hashed_password(plain_password),
        is_superuser=is_superuser,
        is_staff=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_user_password(db: db_dep, user: user_dep, data: ChangePassword):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
    user_db = db.query(User).filter(User.id == user["id"]).first()

    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User Does not match"
        )

    current_plain_password = data.current_password
    plain_password = data.password
    plain_password2 = data.password2
    user_dict = data.model_dump()
    user_dict.pop("password")
    user_dict.pop("password2")

    if not verify_password(current_plain_password, user_db.password):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Password Does not match"
        )

    if plain_password != plain_password2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Password Does not match"
        )

    user_db.password = get_hashed_password(plain_password)  # type: ignore
    db.add(user_db)
    db.commit()


@router.put("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(
    db: db_dep,
    user: user_dep,
    data: UserUpdate,
    user_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found"
        )

    # Check if username already exists
    if data.username and data.username != user.username:
        existing_user = db.query(User).filter(User.username == data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

    # Check if email already exists
    if data.email:
        if data.email and data.email != user.email:
            existing_user = db.query(User).filter(User.email == data.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists",
                )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
