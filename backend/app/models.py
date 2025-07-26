"""SQLAlchemy‑Modelle für das Buchhaltungssystem.

Diese Modelle bilden die grundlegenden Entitäten ab: Kunden, Belege,
Umsatzsteuervoranmeldungen und offene Posten.  Die Felder sind bewusst
einfach gehalten; für produktive Systeme sollten Indizes,
Default‑Werte und Constraints ergänzt werden.
"""

from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    vat_id = Column(String(50), nullable=True)  # USt‑ID

    receipts = relationship("Receipt", back_populates="customer", cascade="all, delete-orphan")
    ustva = relationship("Ustva", back_populates="customer", cascade="all, delete-orphan")
    open_items = relationship("OpenItem", back_populates="customer", cascade="all, delete-orphan")


class Receipt(Base):
    __tablename__ = "receipts"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    file_path = Column(String(512), nullable=False)  # Pfad in S3/Storage
    date = Column(Date, nullable=True)
    net_amount = Column(Numeric(10, 2), nullable=True)
    tax_amount = Column(Numeric(10, 2), nullable=True)
    gross_amount = Column(Numeric(10, 2), nullable=True)
    supplier = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="receipts")


class Ustva(Base):
    __tablename__ = "ustva"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    period = Column(String(7), nullable=False)  # Format: YYYY-MM
    net_sum = Column(Numeric(12, 2), nullable=False)
    tax_sum = Column(Numeric(12, 2), nullable=False)
    gross_sum = Column(Numeric(12, 2), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="ustva")


class OpenItem(Base):
    __tablename__ = "open_items"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    due_date = Column(Date, nullable=False)
    paid = Column(Boolean, default=False, nullable=False)

    customer = relationship("Customer", back_populates="open_items")