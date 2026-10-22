from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.create_product(payload)

@router.get("", response_model=List[ProductResponse])
def search_products(
    name: Optional[str] = Query(None),
    minPrice: Optional[Decimal] = Query(None),
    maxPrice: Optional[Decimal] = Query(None),
    categoryId: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.search_products(
        name=name,
        min_price=minPrice,
        max_price=maxPrice,
        category_id=categoryId,
    )
