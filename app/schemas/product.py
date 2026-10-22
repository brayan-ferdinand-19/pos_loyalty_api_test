from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)
    unit_price: Decimal = Field(..., gt=0, alias="unitPrice")
    available_quantity: int = Field(0, ge=0, alias="availableQuantity")
    active: bool = True
    category_id: int = Field(..., gt=0, alias="categoryId")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("name", "code")
    @classmethod
    def strip_strings(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Field cannot be empty")
        return trimmed

class ProductResponse(BaseModel):
    product_id: int = Field(..., alias="productId")
    product_code: str = Field(..., alias="productCode")
    product_name: str = Field(..., alias="productName")
    unit_price: Decimal = Field(..., alias="unitPrice")
    available_quantity: int = Field(..., alias="availableQuantity")
    active: bool
    category_id: int = Field(..., alias="categoryId")
    category_name: str = Field(..., alias="categoryName")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
