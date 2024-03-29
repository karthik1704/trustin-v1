from typing import Annotated
from fastapi import APIRouter, Depends, Path, status, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.utils import get_unique_code
from ..schemas.samples import ProductCreate
from app.database import get_db
from ..models.samples import Product

router = APIRouter(prefix="/products", tags=["Products"])

db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_products(db: db_dep, user: user_dep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    products = db.query(Product).all()

    return products

@router.get("/trf", status_code=status.HTTP_200_OK)
async def get_all_products_for_trf(db: db_dep):

    products = db.query(Product).all()

    return products

@router.get('/{product_id}', status_code=status.HTTP_200_OK)
async def get_product(db:db_dep, user:user_dep, product_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    product = db.query(Product).filter(Product.id==product_id).first()

    return product

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(db: db_dep, data: ProductCreate, user: user_dep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    product.product_code = get_unique_code('SAM', product.id) # type: ignore
    db.commit()


@router.put("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_product(
    db: db_dep,
    user: user_dep,
    data: ProductCreate,
    product_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    product = (
        db.query(Product).filter(Product.id == product_id).first()
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product Not Found"
        )

     

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)


    db.commit()
    db.refresh(product)