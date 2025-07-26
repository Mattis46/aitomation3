"""UStVA calculation utilities.

This module provides a single function :func:`calculate_ustva` which
aggregates receipt data for a given customer and month.  The function
returns a dictionary containing the sales tax (``umsatzsteuer``), the
input tax (``vorsteuer``) and the resulting amount payable to the
German tax authorities (``zahllast``).  It also returns the
formatted month string (``monat``).  The calculations operate on
SQLAlchemy models defined in :mod:`app.models` and accept either an
existing database session or create a new one on demand.

Example usage::

    from app.ustva_engine import calculate_ustva
    result = calculate_ustva(customer_id=1, year=2025, month=7)
    print(result["zahllast"])

Note that this implementation assumes all receipts represent revenue.
In a real system you should distinguish between outgoing (sales)
invoices and incoming (purchase) invoices to correctly separate
``umsatzsteuer`` from ``vorsteuer``.
"""

from __future__ import annotations

import calendar
import logging
from datetime import date
from decimal import Decimal
from typing import Dict, Optional, Iterable

from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Receipt


def _get_date_range(year: int, month: int) -> tuple[date, date]:
    """Return the start and end date for a given month.

    Args:
        year: A four digit year (e.g. 2025)
        month: A month between 1 and 12

    Returns:
        A tuple ``(start_date, end_date)`` where ``start_date`` is the
        first day of the month and ``end_date`` is the last day of the
        month.
    """
    start_date = date(year, month, 1)
    # `monthrange` returns (weekday, number_of_days)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    return start_date, end_date


def calculate_ustva(
    customer_id: int,
    year: int,
    month: int,
    db: Optional[Session] = None,
) -> Dict[str, Decimal | str]:
    """Aggregate receipts and compute UStVA sums for one customer and period.

    Args:
        customer_id: ID of the customer whose receipts should be processed.
        year: The year of the period.
        month: The month of the period (1–12).
        db: Optional SQLAlchemy session.  When omitted a new session is
            created via :func:`~app.database.SessionLocal` and closed
            automatically.

    Returns:
        A dictionary with the following keys:

            ``monat`` – a string formatted as YYYY-MM
            ``umsatzsteuer`` – total VAT collected from sales (Decimal)
            ``vorsteuer`` – total input tax from purchases (Decimal)
            ``zahllast`` – tax liability (Decimal) calculated as
            ``umsatzsteuer - vorsteuer``

    Note:
        This simplified implementation treats every receipt as a sales
        invoice and therefore sets ``vorsteuer`` to zero.  Modify the
        logic to separate incoming and outgoing receipts in a real
        application.
    """
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True
    try:
        start_date, end_date = _get_date_range(year, month)
        # Query all receipts for the given customer and period
        receipts: Iterable[Receipt] = (
            db.query(Receipt)
            .filter(
                Receipt.customer_id == customer_id,
                Receipt.date >= start_date,
                Receipt.date <= end_date,
            )
            .all()
        )
        # Sum up amounts using Decimal to maintain precision
        net_sum = Decimal("0.00")
        tax_sum = Decimal("0.00")
        gross_sum = Decimal("0.00")
        for rec in receipts:
            if rec.net_amount:
                net_sum += Decimal(rec.net_amount)
            if rec.tax_amount:
                tax_sum += Decimal(rec.tax_amount)
            if rec.gross_amount:
                gross_sum += Decimal(rec.gross_amount)
        # For this simple example treat all tax as sales tax
        umsatzsteuer = tax_sum
        vorsteuer = Decimal("0.00")
        zahllast = umsatzsteuer - vorsteuer
        period_str = f"{year:04d}-{month:02d}"
        return {
            "monat": period_str,
            "umsatzsteuer": umsatzsteuer.quantize(Decimal("0.01")),
            "vorsteuer": vorsteuer.quantize(Decimal("0.01")),
            "zahllast": zahllast.quantize(Decimal("0.01")),
        }
    finally:
        if own_session:
            db.close()