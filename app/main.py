from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.core.exceptions import AppException, app_exception_handler, validation_exception_handler
from app.db.base import Base
from app.db.session import engine
from app.routers import products, orders, loyalty_customers, sales

# Create database tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Register API routers with /api/v1 prefix
app.include_router(products.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(loyalty_customers.router, prefix="/api/v1")
app.include_router(sales.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "POS Orders & Customer Loyalty API is running"}
