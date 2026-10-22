from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class DailySalesSummaryResponse(BaseModel):
    date: str
    completed_order_count: int = Field(..., alias="completedOrderCount")
    total_units_sold: int = Field(..., alias="totalUnitsSold")
    total_sales_revenue: Decimal = Field(..., alias="totalSalesRevenue")
    total_loyalty_points_earned: int = Field(..., alias="totalLoyaltyPointsEarned")

    model_config = ConfigDict(populate_by_name=True)
