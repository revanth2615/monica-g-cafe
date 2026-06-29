"""
One-time script to create the very first admin account, plus a couple
of sample categories/menu items so the frontend has something to show
right after setup.

Run with:  python seed.py
"""
from app.database import SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.models.menu import Category, MenuItem
from app.models.inventory import InventoryItem

Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    # --- Admin account ---
    admin_email = "admin@monikagcafe.com"
    if not db.query(User).filter(User.email == admin_email).first():
        admin = User(
            name="Monika G",
            email=admin_email,
            phone="+910000000000",
            role=UserRole.admin,
            is_verified=True,
        )
        db.add(admin)
        print(f"Created admin account: {admin_email} (log in via email OTP or mobile OTP)")
    else:
        print("Admin account already exists.")

    # --- Sample categories + menu items ---
    if db.query(Category).count() == 0:
        beverages = Category(name="Beverages")
        snacks = Category(name="Snacks")
        db.add_all([beverages, snacks])
        db.flush()

        db.add_all([
            MenuItem(name="Cappuccino", description="Espresso with steamed milk foam", price=120, category_id=beverages.id),
            MenuItem(name="Cold Coffee", description="Iced coffee blended with milk", price=140, category_id=beverages.id),
            MenuItem(name="Veg Sandwich", description="Grilled sandwich with fresh vegetables", price=90, category_id=snacks.id),
            MenuItem(name="French Fries", description="Crispy salted fries", price=110, category_id=snacks.id),
        ])
        print("Added sample menu items.")

    # --- Sample inventory ---
    if db.query(InventoryItem).count() == 0:
        db.add_all([
            InventoryItem(name="Coffee Beans", unit="kg", quantity_in_stock=10, reorder_level=2, cost_per_unit=800),
            InventoryItem(name="Milk", unit="ltr", quantity_in_stock=20, reorder_level=5, cost_per_unit=60),
            InventoryItem(name="Bread", unit="pcs", quantity_in_stock=50, reorder_level=10, cost_per_unit=5),
        ])
        print("Added sample inventory items.")

    db.commit()
    print("Seeding complete.")
finally:
    db.close()
