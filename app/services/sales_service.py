from datetime import datetime, date, time, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from app.repositories.sales_repository import SalesRepository
from app.schemas.sales import DailySalesSummaryResponse
from app.core.config import settings
from app.core.exceptions import BadRequestException

class SalesService:
    def __init__(self, db: Session):
        self.repo = SalesRepository(db)

    def get_daily_summary(self, date_str: str) -> DailySalesSummaryResponse:
        # Validate date format YYYY-MM-DD
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            raise BadRequestException("Invalid date format. Expected ISO date format: YYYY-MM-DD")

        # Asia/Colombo business day: midnight to next day's midnight
        colombo_tz = ZoneInfo(settings.TIMEZONE)
        start_colombo = datetime.combine(target_date, time.min, tzinfo=colombo_tz)
        end_colombo = start_colombo + timedelta(days=1)

        summary = self.repo.get_daily_summary(start_colombo, end_colombo)

        return DailySalesSummaryResponse(
            date=date_str,
            completedOrderCount=summary["completedOrderCount"],
            totalUnitsSold=summary["totalUnitsSold"],
            totalSalesRevenue=summary["totalSalesRevenue"],
            totalLoyaltyPointsEarned=summary["totalLoyaltyPointsEarned"],
        )
