from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_code = Column(String(50), unique=True, nullable=False)
    category_name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    products = relationship("Product", back_populates="category")
