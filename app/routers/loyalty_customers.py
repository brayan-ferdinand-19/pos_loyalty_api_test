from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.customer import CustomerResponse
from app.services.loyalty_service import LoyaltyService

router = APIRouter(prefix="/loyalty-customers", tags=["Loyalty Customers"])

@router.get("", response_model=CustomerResponse)
def get_loyalty_customer(
    mobileNumber: str = Query(..., description="Mobile number: 07XXXXXXXX or +947XXXXXXXX"),
    db: Session = Depends(get_db),
):
    service = LoyaltyService(db)
    return service.get_customer_by_mobile(mobileNumber)
