"""
backend/app/database.py
-----------------------

Stellt Engine, SessionFactory und Base für SQLAlchemy bereit.
Die Datenbank‑URL wird ausschließlich aus der Environment‑Variable
DATABASE_URL gelesen (z. B. von Render). Existiert sie nicht,
stoppt das Programm mit einer klaren Fehlermeldung.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --------------------------------------------------------------------
# 1. DATABASE_URL aus Environment lesen
# --------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "❌  DATABASE_URL ist nicht gesetzt! "
        "Lege sie im Render‑Dashboard unter Service → Environment an."
    )

# --------------------------------------------------------------------
# 2. Engine erstellen
#    pool_pre_ping=True verhindert Idle‑Timeouts in der Cloud
# --------------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

# --------------------------------------------------------------------
# 3. SessionFactory konfigurieren
# --------------------------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)

# --------------------------------------------------------------------
# 4. Declarative Base
# --------------------------------------------------------------------
Base = declarative_base()

# --------------------------------------------------------------------
# 5. Dependency für FastAPI‑Endpoints
# --------------------------------------------------------------------
def get_db():
    """Yield‑basierte DB‑Session für FastAPI Depends."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
