from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerResponse, normalize_mobile
from app.models.customer import Customer
from app.core.exceptions import NotFoundException, BadRequestException

class LoyaltyService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CustomerRepository(db)

    def get_customer_by_mobile(self, raw_mobile: str) -> CustomerResponse:
        try:
            canonical_mobile = normalize_mobile(raw_mobile)
        except ValueError as e:
            raise BadRequestException(str(e))

        customer = self.repo.get_by_mobile(canonical_mobile)
        if not customer:
            raise NotFoundException(f"Loyalty customer with mobile {canonical_mobile} not found")

        return CustomerResponse.model_validate(customer)

    def get_or_enroll_customer_for_order(
        self, full_name: str, raw_mobile: str, email: Optional[str] = None
    ) -> Customer:
        canonical_mobile = normalize_mobile(raw_mobile)
        
        # Use row-level lock for existing customer
        customer = self.repo.get_by_mobile_for_update(canonical_mobile)
        if not customer:
            # Create new customer with 0 points
            customer = Customer(
                mobile_number=canonical_mobile,
                full_name=full_name,
                email=email,
                loyalty_points=0,
            )
            customer = self.repo.create(customer)
        # Note: If customer already exists, preserve existing full_name and email
        return customer
