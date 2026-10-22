from datetime import datetime
from decimal import Decimal
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.order import Order
from app.models.order_item import OrderItem

class SalesRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_daily_summary(self, start_dt: datetime, end_dt: datetime) -> Dict[str, Any]:
        # 1. Aggregate orders to avoid multiplying order totals by items
        order_metrics = (
            self.db.query(
                func.count(Order.order_id).label("order_count"),
                func.coalesce(func.sum(Order.total_amount), 0).label("revenue"),
                func.coalesce(func.sum(Order.loyalty_points_earned), 0).label("points"),
            )
            .filter(
                Order.order_date_time >= start_dt,
                Order.order_date_time < end_dt,
                Order.order_status == "COMPLETED",
            )
            .first()
        )

        # 2. Aggregate item quantities for completed orders within the window
        units_metric = (
            self.db.query(
                func.coalesce(func.sum(OrderItem.quantity), 0).label("units_sold")
            )
            .join(Order, OrderItem.order_id == Order.order_id)
            .filter(
                Order.order_date_time >= start_dt,
                Order.order_date_time < end_dt,
                Order.order_status == "COMPLETED",
            )
            .first()
        )

        order_count = order_metrics.order_count if order_metrics else 0
        revenue = Decimal(str(order_metrics.revenue)) if order_metrics else Decimal("0.00")
        points = int(order_metrics.points) if order_metrics else 0
        units_sold = int(units_metric.units_sold) if units_metric else 0

        return {
            "completedOrderCount": order_count,
            "totalUnitsSold": units_sold,
            "totalSalesRevenue": revenue,
            "totalLoyaltyPointsEarned": points,
        }
