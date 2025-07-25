"""Pydantic‑Schemas für die API.

Die Pydantic‑Modelle dienen als Serialisierungs‑ und Validierungsschicht zwischen
der FastAPI‑Anwendung und den SQLAlchemy‑Objekten.  Sie verwenden das
konfigurierbare Attribut ``orm_mode``, um SQLAlchemy‑Objekte automatisch in
Pydantic‑Modelle zu konvertieren.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    vat_id: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    id: int

    class Config:
        orm_mode = True


class ReceiptBase(BaseModel):
    date: Optional[date] = None
    net_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    gross_amount: Optional[Decimal] = None
    supplier: Optional[str] = None


class ReceiptCreate(ReceiptBase):
    file_path: str  # Pfad nach Upload
    customer_id: int


class ReceiptRead(ReceiptBase):
    id: int
    file_path: str
    uploaded_at: datetime
    customer_id: int

    class Config:
        orm_mode = True


class UstvaBase(BaseModel):
    period: str  # YYYY-MM
    net_sum: Decimal
    tax_sum: Decimal
    gross_sum: Decimal


class UstvaCreate(UstvaBase):
    customer_id: int


class UstvaRead(UstvaBase):
    id: int
    generated_at: datetime
    customer_id: int

    class Config:
        orm_mode = True


class OpenItemBase(BaseModel):
    description: str
    amount: Decimal
    due_date: date
    paid: bool = False


class OpenItemCreate(OpenItemBase):
    customer_id: int


class OpenItemRead(OpenItemBase):
    id: int
    customer_id: int

    class Config:
        orm_mode = True