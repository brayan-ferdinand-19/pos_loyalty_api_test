import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator

def normalize_mobile(mobile: str) -> str:
    cleaned = re.sub(r"[\s\-]", "", mobile.strip())
    match = re.match(r"^(?:\+94|0)(7\d{8})$", cleaned)
    if not match:
        raise ValueError("Invalid Sri Lankan mobile number. Must be 07XXXXXXXX or +947XXXXXXXX")
    return f"+94{match.group(1)}"

class CustomerBase(BaseModel):
    full_name: str = Field(..., min_length=1, alias="fullName")
    mobile_number: str = Field(..., alias="mobileNumber")
    email: Optional[EmailStr] = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Full name cannot be empty")
        return trimmed

    @field_validator("mobile_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return normalize_mobile(v)

class CustomerResponse(BaseModel):
    customer_id: int = Field(..., alias="customerId")
    mobile_number: str = Field(..., alias="mobileNumber")
    full_name: str = Field(..., alias="fullName")
    email: Optional[str] = None
    loyalty_points: int = Field(..., alias="loyaltyPoints")
    registered_at: datetime = Field(..., alias="registeredAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
