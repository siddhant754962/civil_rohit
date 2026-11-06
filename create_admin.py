import getpass
from app.database import Base, engine, SessionLocal
from app.models import AdminUser
from app.security.authentication import hash_password
Base.metadata.create_all(bind=engine)
username = input("New admin username: ").strip()
if not username: raise SystemExit("Username is required")
p1 = getpass.getpass("New admin password (minimum 12 characters): ")
p2 = getpass.getpass("Confirm password: ")
if len(p1) < 12 or p1 != p2: raise SystemExit("Passwords must match and be at least 12 characters")
with SessionLocal() as db:
    if db.query(AdminUser).filter_by(username=username).first(): raise SystemExit("Username already exists")
    db.add(AdminUser(username=username, password_hash=hash_password(p1))); db.commit()
print("Admin created successfully. Keep these credentials private.")
