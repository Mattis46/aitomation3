"""Scheduler für automatische Erinnerungen.

Dieses Modul initialisiert einen Hintergrund‑Scheduler (APScheduler), der
regelmäßige Aufgaben ausführt:

* **Missing Receipts Reminder** – Am fünften Tag eines Monats (9 Uhr) wird geprüft,
  ob im vorherigen Monat keine Belege hochgeladen wurden.  In diesem Fall
  erhalten die Kunden eine Erinnerungs‑E‑Mail.
* **Payment Reminder** – Täglich wird überprüft, ob offene Posten fällig und
  unbezahlt sind.  Bei überfälligen Rechnungen wird eine Zahlungserinnerung an
  die hinterlegte E‑Mail‑Adresse versandt.

Der Versand erfolgt über Mailjet.  Laut Mailjet API v3.1 muss der JSON‑Body
das Feld ``Messages`` enthalten und Absender, Empfänger und Text‑ oder
HTML‑Inhalt definieren【202248353458367†L68-L96】.
"""

import logging
import os
from datetime import datetime, date, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
import requests

from .database import SessionLocal
from .models import Customer, Receipt, OpenItem


log = logging.getLogger(__name__)


def send_mail(to_email: str, subject: str, text: str) -> None:
    """Sende eine E‑Mail über Mailjet.

    Die API‑Schlüssel werden aus den Umgebungsvariablen ``MAILJET_API_KEY`` und
    ``MAILJET_API_SECRET`` gelesen.
    """
    api_key = os.getenv("MAILJET_API_KEY")
    api_secret = os.getenv("MAILJET_API_SECRET")
    if not api_key or not api_secret:
        log.warning("Mailjet‑Schlüssel nicht gesetzt – E‑Mail wurde nicht gesendet.")
        return
    payload = {
        "Messages": [
            {
                "From": {"Email": "no-reply@example.com", "Name": "Buchhaltung"},
                "To": [{"Email": to_email}],
                "Subject": subject,
                "TextPart": text,
            }
        ]
    }
    response = requests.post(
        "https://api.mailjet.com/v3.1/send",
        auth=(api_key, api_secret),
        json=payload,
        timeout=10,
    )
    if response.status_code >= 400:
        log.error("Mailjet antwortete mit Status %s: %s", response.status_code, response.text)


def send_missing_receipt_reminders() -> None:
    """Erinnerungen für fehlende Belege versenden."""
    db: Session = SessionLocal()
    try:
        today = date.today()
        # Zeitraum des Vormonats
        first_day_this_month = today.replace(day=1)
        last_month_end = first_day_this_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        for customer in db.query(Customer).all():
            # Belege des Kunden im Vormonat zählen
            count = (
                db.query(Receipt)
                .filter(
                    Receipt.customer_id == customer.id,
                    Receipt.date >= last_month_start,
                    Receipt.date <= last_month_end,
                )
                .count()
            )
            if count == 0:
                subject = f"Erinnerung: Bitte Belege für {last_month_start.strftime('%B %Y')} einreichen"
                text = (
                    f"Sehr geehrte/r {customer.name},\n\n"
                    f"wir haben festgestellt, dass für den Zeitraum {last_month_start.strftime('%B %Y')} "
                    "noch keine Belege hochgeladen wurden. Bitte reichen Sie die fehlenden Belege ein, "
                    "damit wir Ihre UStVA korrekt erstellen können.\n\n"
                    "Vielen Dank!"
                )
                send_mail(customer.email, subject, text)
    finally:
        db.close()


def send_payment_reminders() -> None:
    """Zahlungserinnerungen für überfällige offene Posten versenden."""
    db: Session = SessionLocal()
    try:
        today = date.today()
        for item in db.query(OpenItem).filter(OpenItem.paid == False).all():
            if item.due_date < today:
                customer = db.query(Customer).get(item.customer_id)
                subject = f"Zahlungserinnerung: {item.description}"
                days_overdue = (today - item.due_date).days
                text = (
                    f"Sehr geehrte/r {customer.name},\n\n"
                    f"die Rechnung '{item.description}' über {item.amount} EUR war am {item.due_date} fällig "
                    f"und ist seit {days_overdue} Tagen überfällig. Bitte begleichen Sie den offenen Betrag.\n\n"
                    "Mit freundlichen Grüßen"
                )
                send_mail(customer.email, subject, text)
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    """Initialisiere den Scheduler und gebe ihn zurück.

    Der Scheduler wird bei Start der Anwendung gestartet und bleibt im
    Hintergrund aktiv.
    """
    scheduler = BackgroundScheduler(timezone="Europe/Berlin")
    # Am 5. Tag eines jeden Monats um 09:00 Uhr
    scheduler.add_job(
        send_missing_receipt_reminders,
        CronTrigger(day=5, hour=9, minute=0),
        name="MissingReceiptsReminder",
    )
    # Täglich um 08:00 Uhr
    scheduler.add_job(
        send_payment_reminders,
        CronTrigger(hour=8, minute=0),
        name="PaymentReminder",
    )
    scheduler.start()
    log.info("Scheduler gestartet")
    return scheduler