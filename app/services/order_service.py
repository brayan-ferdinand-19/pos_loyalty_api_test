from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.product_repository import ProductRepository
from app.repositories.order_repository import OrderRepository
from app.services.loyalty_service import LoyaltyService
from app.schemas.order import OrderCreate, OrderResponse, OrderItemResponse, OrderCustomerDetail
from app.models.order import Order
from app.models.order_item import OrderItem
from app.core.exceptions import BadRequestException

class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.order_repo = OrderRepository(db)
        self.loyalty_service = LoyaltyService(db)

    def place_order(self, order_data: OrderCreate) -> OrderResponse:
        try:
            # 1. Resolve or enroll customer first
            customer = self.loyalty_service.get_or_enroll_customer_for_order(
                full_name=order_data.customer.full_name,
                raw_mobile=order_data.customer.mobile_number,
                email=order_data.customer.email,
            )

            order_items_to_create = []
            order_items_response = []
            total_amount = Decimal("0.00")

            # 2. Validate products, check stock, and calculate amounts
            for item in order_data.items:
                product = self.product_repo.get_by_id_for_update(item.product_id)
                if not product:
                    raise BadRequestException(f"Product with ID {item.product_id} not found")

                if not product.active:
                    raise BadRequestException(f"Product '{product.product_name}' is inactive and cannot be ordered")

                if product.available_quantity < item.quantity:
                    raise BadRequestException(
                        f"Insufficient stock for '{product.product_name}'. Requested: {item.quantity}, Available: {product.available_quantity}"
                    )

                # Deduct stock
                product.available_quantity -= item.quantity

                subtotal = product.unit_price * item.quantity
                total_amount += subtotal

                order_item = OrderItem(
                    product_id=product.product_id,
                    quantity=item.quantity,
                    unit_price=product.unit_price,
                    subtotal=subtotal,
                )
                order_items_to_create.append(order_item)

                order_items_response.append(
                    OrderItemResponse(
                        productId=product.product_id,
                        productName=product.product_name,
                        quantity=item.quantity,
                        unitPrice=product.unit_price,
                        subtotal=subtotal,
                    )
                )

            # 3. Calculate loyalty points earned: floor(total / 100)
            points_earned = int(total_amount // Decimal("100"))
            customer.loyalty_points += points_earned

            # 4. Create Order record
            order = Order(
                customer_id=customer.customer_id,
                order_date_time=datetime.now(timezone.utc),
                order_status="COMPLETED",
                total_amount=total_amount,
                loyalty_points_earned=points_earned,
                items=order_items_to_create,
            )

            self.order_repo.create(order)
            self.db.commit()
            self.db.refresh(order)
            self.db.refresh(customer)

            return OrderResponse(
                orderId=order.order_id,
                orderDateTime=order.order_date_time,
                orderStatus=order.order_status,
                totalAmount=order.total_amount,
                loyaltyPointsEarned=order.loyalty_points_earned,
                resultingLoyaltyBalance=customer.loyalty_points,
                customer=OrderCustomerDetail(
                    customerId=customer.customer_id,
                    fullName=customer.full_name,
                    mobileNumber=customer.mobile_number,
                    loyaltyPointsBalance=customer.loyalty_points,
                ),
                items=order_items_response,
            )
        except Exception:
            self.db.rollback()
            raise
