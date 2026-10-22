from typing import Optional
from sqlalchemy.orm import Session
from app.models.customer import Customer

class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_mobile(self, mobile_number: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.mobile_number == mobile_number).first()

    def get_by_mobile_for_update(self, mobile_number: str) -> Optional[Customer]:
        query = self.db.query(Customer).filter(Customer.mobile_number == mobile_number)
        if self.db.bind.dialect.name != "sqlite":
            query = query.with_for_update()
        return query.first()

    def create(self, customer: Customer) -> Customer:
        self.db.add(customer)
        self.db.flush()
        return customer
