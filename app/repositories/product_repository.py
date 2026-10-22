from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.product import Product
from app.models.category import Category

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).options(joinedload(Product.category)).filter(Product.product_id == product_id).first()

    def get_by_id_for_update(self, product_id: int) -> Optional[Product]:
        # Lock row for atomic stock update
        query = self.db.query(Product).filter(Product.product_id == product_id)
        if self.db.bind.dialect.name != "sqlite":
            query = query.with_for_update()
        return query.first()

    def get_by_code(self, product_code: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.product_code == product_code).first()

    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        return self.db.query(Category).filter(Category.category_id == category_id).first()

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def search(
        self,
        name: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        category_id: Optional[int] = None,
    ) -> List[Product]:
        query = self.db.query(Product).options(joinedload(Product.category))

        if name:
            query = query.filter(Product.product_name.ilike(f"%{name}%"))
        if min_price is not None:
            query = query.filter(Product.unit_price >= min_price)
        if max_price is not None:
            query = query.filter(Product.unit_price <= max_price)
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)

        return query.all()
