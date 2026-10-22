from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductResponse
from app.models.product import Product
from app.core.exceptions import BadRequestException, ConflictException

class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def create_product(self, data: ProductCreate) -> ProductResponse:
        # Check duplicate product code
        existing = self.repo.get_by_code(data.code)
        if existing:
            raise ConflictException(f"Product with code '{data.code}' already exists")

        # Validate category
        category = self.repo.get_category_by_id(data.category_id)
        if not category:
            raise BadRequestException(f"Category {data.category_id} not found")
        if not category.active:
            raise BadRequestException(f"Category {data.category_id} is inactive")

        product = Product(
            product_code=data.code,
            product_name=data.name,
            unit_price=data.unit_price,
            available_quantity=data.available_quantity,
            active=data.active,
            category_id=data.category_id,
        )
        saved = self.repo.create(product)
        return ProductResponse(
            productId=saved.product_id,
            productCode=saved.product_code,
            productName=saved.product_name,
            unitPrice=saved.unit_price,
            availableQuantity=saved.available_quantity,
            active=saved.active,
            categoryId=category.category_id,
            categoryName=category.category_name,
        )

    def search_products(
        self,
        name: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        category_id: Optional[int] = None,
    ) -> List[ProductResponse]:
        # Validate price range
        if min_price is not None and min_price < 0:
            raise BadRequestException("minPrice must be zero or greater")
        if max_price is not None and max_price < 0:
            raise BadRequestException("maxPrice must be zero or greater")
        if min_price is not None and max_price is not None and min_price > max_price:
            raise BadRequestException("minPrice cannot be greater than maxPrice")

        # Validate categoryId
        if category_id is not None and category_id <= 0:
            raise BadRequestException("categoryId must be a positive integer")

        # Trim name; empty becomes None
        trimmed_name = name.strip() if name else None
        if trimmed_name == "":
            trimmed_name = None

        products = self.repo.search(
            name=trimmed_name,
            min_price=min_price,
            max_price=max_price,
            category_id=category_id,
        )

        return [
            ProductResponse(
                productId=p.product_id,
                productCode=p.product_code,
                productName=p.product_name,
                unitPrice=p.unit_price,
                availableQuantity=p.available_quantity,
                active=p.active,
                categoryId=p.category.category_id,
                categoryName=p.category.category_name,
            )
            for p in products
        ]
