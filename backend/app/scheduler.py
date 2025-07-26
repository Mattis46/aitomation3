"""
backend/app/scheduler.py
------------------------

Initialises an APScheduler instance and registers reminder jobs.  In
addition to the two sample jobs for missing receipts and payment
reminders, this module now includes a third job that calculates
UStVA (VAT pre‑declaration) summaries for each customer and sends a
reminder e‑mail via Mailjet.  The scheduler runs in the European
timezone (``Europe/Berlin``) to match the user's locale.
"""

import calendar
import logging
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from decimal import Decimal
from typing import List

from .database import SessionLocal
from .models import Customer, Ustva, Receipt
from .ustva_engine import calculate_ustva
import os
import requests


# -------------------------------------------------
# Scheduler with European timezone
# -------------------------------------------------
scheduler = BackgroundScheduler(timezone="Europe/Berlin")


# -------------------------------------------------
# Job 1: Missing receipts reminder
# -------------------------------------------------
def missing_receipts_reminder() -> None:
    logging.info("📧 MissingReceiptsReminder ausgeführt um %s", datetime.now())


scheduler.add_job(
    missing_receipts_reminder,
    trigger=CronTrigger(day=5, hour=9, minute=0),
    id="MissingReceiptsReminder",
)


# -------------------------------------------------
# Job 2: Payment reminder
# -------------------------------------------------
def payment_reminder() -> None:
    logging.info("📧 PaymentReminder ausgeführt um %s", datetime.now())


scheduler.add_job(
    payment_reminder,
    trigger=CronTrigger(hour=9, minute=30),
    id="PaymentReminder",
)


# -------------------------------------------------
# Helper: Send e‑mails via Mailjet
# -------------------------------------------------
def _send_mailjet_email(to_email: str, subject: str, html: str) -> None:
    """Send an HTML e‑mail using Mailjet's v3.1 API.

    The API key and secret are read from the environment variables
    ``MJ_APIKEY_PUBLIC`` and ``MJ_APIKEY_PRIVATE``.  Sender address
    information can be configured via ``MAILJET_FROM_EMAIL`` and
    ``MAILJET_FROM_NAME``.  If any credential is missing the function
    logs a warning and returns without making a network request.
    """
    api_key = os.getenv("MJ_APIKEY_PUBLIC")
    api_secret = os.getenv("MJ_APIKEY_PRIVATE")
    from_email = os.getenv("MAILJET_FROM_EMAIL", "no-reply@example.com")
    from_name = os.getenv("MAILJET_FROM_NAME", "Accounting SaaS")
    if not api_key or not api_secret:
        logging.warning("Mailjet credentials are not configured; skipping email to %s", to_email)
        return
    payload = {
        "Messages": [
            {
                "From": {"Email": from_email, "Name": from_name},
                "To": [{"Email": to_email, "Name": to_email}],
                "Subject": subject,
                "HTMLPart": html,
            }
        ]
    }
    try:
        resp = requests.post(
            "https://api.mailjet.com/v3.1/send",
            auth=(api_key, api_secret),
            json=payload,
            timeout=10,
        )
        if resp.status_code >= 400:
            logging.warning("Mailjet send failed (%s): %s", resp.status_code, resp.text)
    except Exception as exc:
        logging.warning("Error sending Mailjet email: %s", exc)


# -------------------------------------------------
# Job 3: UStVA reminder
# -------------------------------------------------
def send_ustva_reminder() -> None:
    """Compute and dispatch UStVA summaries for all customers.

    For the current month, the job checks whether a UStVA record
    already exists for each customer.  If not, it calculates the sums
    using :func:`app.ustva_engine.calculate_ustva`, writes a new
    :class:`app.models.Ustva` entry with net, tax and gross totals and
    sends an HTML e‑mail with the aggregated figures.  Any error
    encountered for a single customer is logged and does not stop
    processing the remaining customers.
    """
    today = date.today()
    period_str = f"{today.year:04d}-{today.month:02d}"
    session = SessionLocal()
    try:
        customers: List[Customer] = session.query(Customer).all()
        for customer in customers:
            try:
                # Skip if UStVA already exists
                existing = (
                    session.query(Ustva)
                    .filter(Ustva.customer_id == customer.id, Ustva.period == period_str)
                    .first()
                )
                if existing:
                    continue
                # Compute summary (sales VAT, input VAT and liability)
                summary = calculate_ustva(customer.id, today.year, today.month, session)
                # Aggregate raw sums for Ustva table
                # Compute date range for the month
                first_day = date(today.year, today.month, 1)
                last_day = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
                receipts = (
                    session.query(Receipt)
                    .filter(
                        Receipt.customer_id == customer.id,
                        Receipt.date >= first_day,
                        Receipt.date <= last_day,
                    )
                    .all()
                )
                net_sum: Decimal = sum((r.net_amount or Decimal("0.00")) for r in receipts)
                tax_sum: Decimal = sum((r.tax_amount or Decimal("0.00")) for r in receipts)
                gross_sum: Decimal = sum((r.gross_amount or Decimal("0.00")) for r in receipts)
                # Create and persist new Ustva entry
                new_entry = Ustva(
                    customer_id=customer.id,
                    period=period_str,
                    net_sum=net_sum,
                    tax_sum=tax_sum,
                    gross_sum=gross_sum,
                )
                session.add(new_entry)
                session.commit()
                # Prepare email content
                subject = f"UStVA {period_str} für {customer.name}"
                html = (
                    f"<h1>UStVA {period_str}</h1>"
                    f"<p>Umsatzsteuer: {summary['umsatzsteuer']}<br/>"
                    f"Vorsteuer: {summary['vorsteuer']}<br/>"
                    f"Zahllast: {summary['zahllast']}</p>"
                )
                _send_mailjet_email(customer.email, subject, html)
            except Exception as exc:
                # Roll back on any failure during processing a single customer
                session.rollback()
                logging.warning(
                    "Failed to process UStVA reminder for customer %s (%s): %s",
                    customer.id,
                    customer.email,
                    exc,
                )
    finally:
        session.close()


# Schedule the UStVA reminder for the 10th of each month at 09:00
scheduler.add_job(
    send_ustva_reminder,
    trigger=CronTrigger(day=10, hour=9, minute=0),
    id="UstvaReminder",
)


__all__ = ["scheduler"]