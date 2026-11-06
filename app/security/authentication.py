from passlib.context import CryptContext
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from app.models import AdminUser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str: return pwd_context.hash(password)
def verify_password(password: str, hashed: str) -> bool: return pwd_context.verify(password, hashed)
def require_admin(request: Request, db: Session) -> AdminUser:
    user_id = request.session.get("admin_id")
    if not user_id: raise HTTPException(status_code=303, headers={"Location": "/admin/login"})
    user = db.get(AdminUser, int(user_id))
    if not user:
        request.session.clear()
        raise HTTPException(status_code=303, headers={"Location": "/admin/login"})
    return user
