import os
from decimal import Decimal
from datetime import date
from fastapi.testclient import TestClient

# Use temporary sqlite database for local test verification
os.environ["DATABASE_URL"] = "sqlite:///./test_pos.db"

from app.main import app
from app.db.base import Base
from app.db.session import engine
from seed import seed_categories

client = TestClient(app)

def run_tests():
    # Reset database schema cleanly
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("=" * 60)
    print("RUNNING VERIFICATION SCENARIOS (POS & LOYALTY API)")
    print("=" * 60)



    # 1. Seed categories
    print("\n[Step 1] Seeding starter categories...")
    seed_categories()

    # 2. Section 8: Create product test fixtures
    print("\n[Step 2] Creating test fixture products via POST /api/v1/products...")
    fixtures = [
        {"name": "Notebook A5", "code": "PRD001", "unitPrice": 350.00, "availableQuantity": 100, "categoryId": 1, "active": True},
        {"name": "Blue Pen", "code": "PRD002", "unitPrice": 80.00, "availableQuantity": 200, "categoryId": 1, "active": True},
        {"name": "Stapler", "code": "PRD003", "unitPrice": 1250.00, "availableQuantity": 25, "categoryId": 2, "active": True},
        {"name": "Paper Pack", "code": "PRD004", "unitPrice": 1800.00, "availableQuantity": 0, "categoryId": 2, "active": True},
        {"name": "Calculator", "code": "PRD005", "unitPrice": 2500.00, "availableQuantity": 10, "categoryId": 3, "active": False},
    ]

    product_ids = {}
    for fix in fixtures:
        res = client.post("/api/v1/products", json=fix)
        assert res.status_code == 201, f"Failed to create {fix['code']}: {res.text}"
        data = res.json()
        product_ids[data["productCode"]] = data["productId"]
        print(f" Created {data['productCode']} -> ID: {data['productId']} ({data['productName']})")

    # Scenario 1: Combined search (name=pen, minPrice=50, maxPrice=100, categoryId=1) -> Blue Pen only
    print("\n[Scenario 1] Combined product search...")
    res = client.get("/api/v1/products?name=pen&minPrice=50&maxPrice=100&categoryId=1")
    assert res.status_code == 200, res.text
    items = res.json()
    assert len(items) == 1 and items[0]["productCode"] == "PRD002", f"Unexpected search result: {items}"
    print(" PASSED: Returned Blue Pen only.")

    # Scenario 2: minPrice=200 and maxPrice=100 -> Validation error
    print("\n[Scenario 2] Invalid price bounds (minPrice > maxPrice)...")
    res = client.get("/api/v1/products?minPrice=200&maxPrice=100")
    assert res.status_code in [400, 422], f"Expected error, got {res.status_code}"
    print(f" PASSED: Rejected with status {res.status_code} ({res.json().get('message')})")

    # Scenario 3: Create product under category 4 (inactive) -> Rejected
    print("\n[Scenario 3] Create product under inactive category 4...")
    bad_prod = {"name": "Old Folder", "code": "PRD006", "unitPrice": 100.00, "availableQuantity": 5, "categoryId": 4, "active": True}
    res = client.post("/api/v1/products", json=bad_prod)
    assert res.status_code in [400, 422], f"Expected failure, got {res.status_code}"
    print(f" PASSED: Rejected as expected ({res.json().get('message')})")

    # Scenario 4: New customer 0771234567; order 2 notebooks and 3 pens
    print("\n[Scenario 4] New customer 0771234567 places multi-item order (2 Notebooks + 3 Pens)...")
    order_payload = {
        "customer": {
            "fullName": "Kasun Perera",
            "mobileNumber": "0771234567",
            "email": "kasun@example.com"
        },
        "items": [
            {"productId": product_ids["PRD001"], "quantity": 2},
            {"productId": product_ids["PRD002"], "quantity": 3}
        ]
    }
    res = client.post("/api/v1/orders", json=order_payload)
    assert res.status_code == 201, res.text
    order_data = res.json()
    assert Decimal(str(order_data["totalAmount"])) == Decimal("940.00"), f"Expected 940.00, got {order_data['totalAmount']}"
    assert order_data["loyaltyPointsEarned"] == 9, f"Expected 9 points, got {order_data['loyaltyPointsEarned']}"
    assert order_data["resultingLoyaltyBalance"] == 9
    assert order_data["customer"]["mobileNumber"] == "+94771234567"
    print(f" PASSED: Order total Rs {order_data['totalAmount']}, Points {order_data['loyaltyPointsEarned']}, Customer {order_data['customer']['mobileNumber']}")

    # Verify stock reduction
    res_p1 = client.get(f"/api/v1/products?categoryId=1")
    p1 = next(p for p in res_p1.json() if p["productCode"] == "PRD001")
    p2 = next(p for p in res_p1.json() if p["productCode"] == "PRD002")
    assert p1["availableQuantity"] == 98, f"Expected 98, got {p1['availableQuantity']}"
    assert p2["availableQuantity"] == 197, f"Expected 197, got {p2['availableQuantity']}"
    print(f" PASSED: Stocks reduced correctly to 98 and 197.")

    # Scenario 5: Same customer +94771234567; order 1 stapler
    print("\n[Scenario 5] Existing customer orders 1 Stapler...")
    order_payload_2 = {
        "customer": {
            "fullName": "Kasun P.", # Should not overwrite Kasun Perera
            "mobileNumber": "+94771234567"
        },
        "items": [
            {"productId": product_ids["PRD003"], "quantity": 1}
        ]
    }
    res = client.post("/api/v1/orders", json=order_payload_2)
    assert res.status_code == 201, res.text
    order_data_2 = res.json()
    assert Decimal(str(order_data_2["totalAmount"])) == Decimal("1250.00")
    assert order_data_2["loyaltyPointsEarned"] == 12
    assert order_data_2["resultingLoyaltyBalance"] == 21
    print(f" PASSED: Order total Rs {order_data_2['totalAmount']}, Points {order_data_2['loyaltyPointsEarned']}, Total balance {order_data_2['resultingLoyaltyBalance']}")

    # Scenario 6: Lookup 0771234567 after both orders
    print("\n[Scenario 6] Lookup loyalty customer by mobile 0771234567...")
    res = client.get("/api/v1/loyalty-customers?mobileNumber=0771234567")
    assert res.status_code == 200, res.text
    cust = res.json()
    assert cust["fullName"] == "Kasun Perera" # preserved original name
    assert cust["loyaltyPoints"] == 21
    assert cust["mobileNumber"] == "+94771234567"
    print(f" PASSED: Customer profile preserved, total points = {cust['loyaltyPoints']}")

    # Scenario 7: Order notebook plus unavailable Paper Pack (stock 0) -> Fail & rollback
    print("\n[Scenario 7] Order item with insufficient stock (Paper Pack)...")
    fail_order = {
        "customer": {"fullName": "Kasun Perera", "mobileNumber": "0771234567"},
        "items": [
            {"productId": product_ids["PRD001"], "quantity": 1},
            {"productId": product_ids["PRD004"], "quantity": 1}
        ]
    }
    res = client.post("/api/v1/orders", json=fail_order)
    assert res.status_code in [400, 422], f"Expected failure, got {res.status_code}"
    # Verify Notebook stock did NOT decrease from 98
    res_p1 = client.get(f"/api/v1/products?categoryId=1")
    p1 = next(p for p in res_p1.json() if p["productCode"] == "PRD001")
    assert p1["availableQuantity"] == 98, "Rollback failed: stock was deducted!"
    print(f" PASSED: Entire order rejected and rolled back ({res.json().get('message')})")

    # Scenario 8: Order inactive Calculator -> Rejected
    print("\n[Scenario 8] Order inactive Calculator...")
    res = client.post("/api/v1/orders", json={
        "customer": {"fullName": "Kasun Perera", "mobileNumber": "0771234567"},
        "items": [{"productId": product_ids["PRD005"], "quantity": 1}]
    })
    assert res.status_code in [400, 422], f"Expected failure, got {res.status_code}"
    print(f" PASSED: Inactive product rejected ({res.json().get('message')})")

    # Scenario 9: Duplicate product IDs in order request -> Rejected
    print("\n[Scenario 9] Duplicate product ID in single order...")
    res = client.post("/api/v1/orders", json={
        "customer": {"fullName": "Kasun Perera", "mobileNumber": "0771234567"},
        "items": [
            {"productId": product_ids["PRD001"], "quantity": 1},
            {"productId": product_ids["PRD001"], "quantity": 2}
        ]
    })
    assert res.status_code in [400, 422], f"Expected failure, got {res.status_code}"
    print(f" PASSED: Duplicate product rejected ({res.json().get('message')})")

    # Scenario 10: Daily Sales Summary
    print("\n[Scenario 10] Daily Sales Summary for today...")
    today_str = date.today().isoformat()
    res = client.get(f"/api/v1/sales/summary?date={today_str}")
    assert res.status_code == 200, res.text
    summary = res.json()
    assert summary["completedOrderCount"] == 2, f"Expected 2 orders, got {summary['completedOrderCount']}"
    assert summary["totalUnitsSold"] == 6, f"Expected 6 units (2+3+1), got {summary['totalUnitsSold']}"
    assert Decimal(str(summary["totalSalesRevenue"])) == Decimal("2190.00"), f"Expected 2190.00, got {summary['totalSalesRevenue']}"
    assert summary["totalLoyaltyPointsEarned"] == 21, f"Expected 21 points, got {summary['totalLoyaltyPointsEarned']}"
    print(f" PASSED: 2 orders, 6 units sold, Rs 2,190.00 revenue, 21 loyalty points!")

    # Scenario 11: Day without completed orders
    print("\n[Scenario 11] Day without completed orders (2020-01-01)...")
    res = client.get("/api/v1/sales/summary?date=2020-01-01")
    assert res.status_code == 200, res.text
    empty_summary = res.json()
    assert empty_summary["completedOrderCount"] == 0
    assert empty_summary["totalUnitsSold"] == 0
    assert Decimal(str(empty_summary["totalSalesRevenue"])) == Decimal("0.00")
    assert empty_summary["totalLoyaltyPointsEarned"] == 0
    print(" PASSED: All metrics are zero.")

    print("\n" + "=" * 60)
    print("ALL 11 VERIFICATION SCENARIOS PASSED SUCCESSFULLY!")
    print("=" * 60)

    # Cleanup tables
    Base.metadata.drop_all(bind=engine)

if __name__ == "__main__":
    run_tests()

