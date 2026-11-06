from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Boolean, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

def now(): return datetime.now(timezone.utc)

class AdminUser(Base):
    __tablename__ = "admin_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Enquiry(Base):
    __tablename__ = "enquiries"
    __table_args__ = (Index("ix_enquiry_status_created", "status", "created_at"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254))
    phone: Mapped[str] = mapped_column(String(30))
    service: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(180))
    project_type: Mapped[str] = mapped_column(String(100))
    budget: Mapped[str | None] = mapped_column(String(80), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    attachment_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    preferred_contact: Mapped[str] = mapped_column(String(30), default="Email")
    status: Mapped[str] = mapped_column(String(30), default="New", index=True)
    admin_notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(80), index=True)
    description: Mapped[str] = mapped_column(Text)
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location: Mapped[str | None] = mapped_column(String(180), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    is_illustrative: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class Service(Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str] = mapped_column(Text)
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class WebsiteSettings(Base):
    __tablename__ = "website_settings"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_name: Mapped[str] = mapped_column(String(120), default="DynamicBuilds")
    company_email: Mapped[str] = mapped_column(String(254), default="patelrohit52525@gmail.com")
    company_phone: Mapped[str] = mapped_column(String(30), default="+91 8252042824")
    founder_name: Mapped[str] = mapped_column(String(120), default="Er. Rohit Kumar")
    founder_linkedin: Mapped[str] = mapped_column(String(300), default="https://www.linkedin.com/in/rohit-kumar-2374ba243/")
    company_description: Mapped[str] = mapped_column(Text, default="Building planning, engineering and architectural consultancy.")
