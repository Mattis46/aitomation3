"""Einstiegspunkt für das Backend.

Dieses Modul instanziiert die FastAPI‑App, bindet die Routen und startet den
Scheduler.  Beim Start werden die Datenbanktabellen erstellt (nur zu
Demonstrationszwecken).  In produktiven Umgebungen sollte die Migration über
Alembic erfolgen.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .api import router as api_router
from .scheduler import start_scheduler

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Accounting SaaS", version="0.1.0")

# CORS für lokale Entwicklung
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Datenbanktabellen erstellen
Base.metadata.create_all(bind=engine)

# API‑Routen einbinden
app.include_router(api_router)

# Scheduler starten
scheduler = start_scheduler()


@app.on_event("shutdown")
def shutdown_event():
    """Scheduler beim Shutdown stoppen."""
    scheduler.shutdown()