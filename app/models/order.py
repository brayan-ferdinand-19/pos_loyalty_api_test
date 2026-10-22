from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Order(Base):
    __tablename__ = "customer_orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    order_date_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    order_status = Column(String(20), default="COMPLETED", nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    loyalty_points_earned = Column(Integer, default=0, nullable=False)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
