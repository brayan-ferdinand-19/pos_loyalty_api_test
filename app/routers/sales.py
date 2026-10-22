from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.sales import DailySalesSummaryResponse
from app.services.sales_service import SalesService

router = APIRouter(prefix="/sales", tags=["Sales"])

@router.get("/summary", response_model=DailySalesSummaryResponse)
def get_sales_summary(
    date: str = Query(..., description="Business date in ISO format YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    service = SalesService(db)
    return service.get_daily_summary(date)
