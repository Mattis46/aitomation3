"""
backend/app/main.py
-------------------

FastAPI-Anwendung inkl.:
* CORS-Middleware für Frontend bei Render + lokales Dev-Frontend
* Datenbanktabellen anlegen (SQLAlchemy)
* APScheduler-Startup
* API-Router einbinden
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# -------------------------- Datenbank --------------------------
from .database import Base, engine
Base.metadata.create_all(bind=engine)  # produktiv via Alembic migrieren

# -------------------------- FastAPI ----------------------------
app = FastAPI(
    title="Accounting SaaS",
    version="0.1.0",
)

# -------------------------- CORS -------------------------------
origins = [
    "https://acct-frontend.onrender.com",  # Render-Frontend
    "http://localhost:5173",               # lokales Vite-Dev-Frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------- API-Router -------------------------
from .api import router as api_router  # noqa: E402  (nach FastAPI-Init importieren)
app.include_router(api_router)

# -------------------------- Scheduler --------------------------
from .scheduler import scheduler  # noqa: E402

@app.on_event("startup")
async def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.start()
        logging.info("Scheduler gestartet")

@app.on_event("shutdown")
async def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()
        logging.info("Scheduler gestoppt")
