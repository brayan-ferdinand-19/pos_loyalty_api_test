from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    product_name = Column(String(150), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    available_quantity = Column(Integer, default=0, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)

    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

    __table_args__ = (
        CheckConstraint("unit_price > 0", name="check_product_unit_price_positive"),
        CheckConstraint("available_quantity >= 0", name="check_product_stock_nonnegative"),
    )
