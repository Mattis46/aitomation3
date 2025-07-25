"""
backend/app/scheduler.py
------------------------

Initialisiert einen APScheduler (Hintergrund) und registriert zwei Jobs:
* MissingReceiptsReminder – 5. Tag des Monats, 09:00 Uhr
* PaymentReminder        – täglich, 09:30 Uhr

FastAPI holt sich das Objekt via:
    from .scheduler import scheduler
"""

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# -------------------------------------------------
# Scheduler mit europäischer Zeitzone
# -------------------------------------------------
scheduler = BackgroundScheduler(timezone="Europe/Berlin")

# -------------------------------------------------
# Job 1: Beleg-Erinnerung
# -------------------------------------------------
def missing_receipts_reminder() -> None:
    logging.info("📧 MissingReceiptsReminder ausgeführt um %s", datetime.now())

scheduler.add_job(
    missing_receipts_reminder,
    trigger=CronTrigger(day=5, hour=9, minute=0),
    id="MissingReceiptsReminder",
)

# -------------------------------------------------
# Job 2: Zahlungs-Erinnerung
# -------------------------------------------------
def payment_reminder() -> None:
    logging.info("📧 PaymentReminder ausgeführt um %s", datetime.now())

scheduler.add_job(
    payment_reminder,
    trigger=CronTrigger(hour=9, minute=30),
    id="PaymentReminder",
)

# -------------------------------------------------
# Nur das Scheduler-Objekt exportieren
# -------------------------------------------------
__all__ = ["scheduler"]
