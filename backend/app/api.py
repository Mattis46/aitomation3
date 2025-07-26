"""FastAPI‑Router für die Geschäftsvorgänge.

Diese Datei definiert die REST‑Endpunkte des Buchhaltungssystems.  Belege
werden per Multipart‑Upload hochgeladen, mit der OCR‑Funktion analysiert
und in der Datenbank gespeichert.  UStVA‑Berechnungen summieren die
Netto‑ und Steuerbeträge der Belege eines Zeitraums.
"""

import os
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .database import get_db
from . import models, schemas, ocr

router = APIRouter()


@router.post("/customers", response_model=schemas.CustomerRead)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.email == customer.email).first()
    if db_customer:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_customer = models.Customer(**customer.dict())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


@router.get("/customers", response_model=list[schemas.CustomerRead])
def list_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).all()


@router.post("/receipts/upload", response_model=schemas.ReceiptRead)
async def upload_receipt(
    customer_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Ensure that the customer exists
    customer = db.query(models.Customer).get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    # Create a temporary upload directory
    uploads_dir = os.getenv("UPLOADS_DIR", "/tmp/uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    file_path = os.path.join(uploads_dir, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    # OCR analyse
    parsed = ocr.parse_receipt_pdf(file_path)
    # Save receipt in database
    receipt = models.Receipt(
        customer_id=customer_id,
        file_path=file_path,
        date=date.fromisoformat(parsed["date"]) if parsed["date"] else None,
        net_amount=parsed["net_amount"],
        tax_amount=parsed["tax_amount"],
        gross_amount=parsed["gross_amount"],
        supplier=parsed["supplier"],
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


@router.get("/receipts", response_model=list[schemas.ReceiptRead])
def list_receipts(customer_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Receipt)
    if customer_id:
        query = query.filter(models.Receipt.customer_id == customer_id)
    return query.all()


@router.post("/ustva/generate/{customer_id}/{period}", response_model=schemas.UstvaRead)
def generate_ustva(customer_id: int, period: str, db: Session = Depends(get_db)):
    """Berechne Summen für die UStVA eines Monats (YYYY-MM)."""
    # Prüfen, ob UStVA für Zeitraum bereits existiert
    existing = (
        db.query(models.Ustva)
        .filter(models.Ustva.customer_id == customer_id, models.Ustva.period == period)
        .first()
    )
    if existing:
        return existing
    # Zeitraum bestimmen
    try:
        year, month = map(int, period.split("-"))
        start_date = date(year, month, 1)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid period format")
    # Ende des Monats berechnen
    if month == 12:
        end_date = date(year + 1, 1, 1) - date.resolution
    else:
        end_date = date(year, month + 1, 1) - date.resolution
    receipts = (
        db.query(models.Receipt)
        .filter(
            models.Receipt.customer_id == customer_id,
            models.Receipt.date >= start_date,
            models.Receipt.date <= end_date,
        )
        .all()
    )
    net_sum = sum((r.net_amount or 0) for r in receipts)
    tax_sum = sum((r.tax_amount or 0) for r in receipts)
    gross_sum = sum((r.gross_amount or 0) for r in receipts)
    ustva_entry = models.Ustva(
        customer_id=customer_id,
        period=period,
        net_sum=net_sum,
        tax_sum=tax_sum,
        gross_sum=gross_sum,
    )
    db.add(ustva_entry)
    db.commit()
    db.refresh(ustva_entry)
    return ustva_entry


@router.get("/ustva/{customer_id}", response_model=list[schemas.UstvaRead])
def list_ustva(customer_id: int, db: Session = Depends(get_db)):
    return db.query(models.Ustva).filter(models.Ustva.customer_id == customer_id).all()


@router.post("/open-items", response_model=schemas.OpenItemRead)
def create_open_item(item: schemas.OpenItemCreate, db: Session = Depends(get_db)):
    new_item = models.OpenItem(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/open-items", response_model=list[schemas.OpenItemRead])
def list_open_items(customer_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.OpenItem)
    if customer_id:
        query = query.filter(models.OpenItem.customer_id == customer_id)
    return query.all()