from decimal import Decimal
from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.schemas.customer import CustomerBase

class OrderItemCreate(BaseModel):
    product_id: int = Field(..., gt=0, alias="productId")
    quantity: int = Field(..., gt=0)

    model_config = ConfigDict(populate_by_name=True)

class OrderCreate(BaseModel):
    customer: CustomerBase
    items: List[OrderItemCreate] = Field(..., min_length=1)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("items")
    @classmethod
    def validate_no_duplicate_products(cls, items: List[OrderItemCreate]) -> List[OrderItemCreate]:
        product_ids = [item.product_id for item in items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Duplicate product IDs found in order items")
        return items

class OrderItemResponse(BaseModel):
    product_id: int = Field(..., alias="productId")
    product_name: str = Field(..., alias="productName")
    quantity: int
    unit_price: Decimal = Field(..., alias="unitPrice")
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class OrderCustomerDetail(BaseModel):
    customer_id: int = Field(..., alias="customerId")
    full_name: str = Field(..., alias="fullName")
    mobile_number: str = Field(..., alias="mobileNumber")
    loyalty_points_balance: int = Field(..., alias="loyaltyPointsBalance")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class OrderResponse(BaseModel):
    order_id: int = Field(..., alias="orderId")
    order_date_time: datetime = Field(..., alias="orderDateTime")
    order_status: str = Field(..., alias="orderStatus")
    total_amount: Decimal = Field(..., alias="totalAmount")
    loyalty_points_earned: int = Field(..., alias="loyaltyPointsEarned")
    resulting_loyalty_balance: int = Field(..., alias="resultingLoyaltyBalance")
    customer: OrderCustomerDetail
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
