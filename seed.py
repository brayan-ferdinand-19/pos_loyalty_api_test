from sqlalchemy import text
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.category import Category

SEED_CATEGORIES = [
    {"id": 1, "code": "STATIONERY", "name": "Stationery", "active": True},
    {"id": 2, "code": "OFFICE", "name": "Office Supplies", "active": True},
    {"id": 3, "code": "ELECTRONICS", "name": "Electronics", "active": True},
    {"id": 4, "code": "ARCHIVED", "name": "Archived Range", "active": False},
]

def seed_categories():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for item in SEED_CATEGORIES:
            existing = db.query(Category).filter(
                (Category.category_id == item["id"]) | (Category.category_code == item["code"])
            ).first()

            if not existing:
                cat = Category(
                    category_id=item["id"],
                    category_code=item["code"],
                    category_name=item["name"],
                    active=item["active"],
                )
                db.add(cat)
            else:
                existing.category_name = item["name"]
                existing.active = item["active"]

        db.commit()

        # Update PostgreSQL sequence if using Postgres
        if db.bind.dialect.name == "postgresql":
            db.execute(text("SELECT setval(pg_get_serial_sequence('categories', 'category_id'), (SELECT COALESCE(MAX(category_id), 1) FROM categories));"))
            db.commit()

        print("Category seed completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding categories: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_categories()
