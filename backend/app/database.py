"""
backend/app/database.py
-----------------------

Stellt Engine, SessionFactory und Base für SQLAlchemy bereit.
Die Datenbank‑URL wird ausschließlich aus der Environment‑Variable
``DATABASE_URL`` gelesen (z. B. von Render).  Existiert sie nicht,
stoppt das Programm mit einer klaren Fehlermeldung.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --------------------------------------------------------------------
# 1. Read DATABASE_URL from environment
# --------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "❌  DATABASE_URL ist nicht gesetzt! "
        "Lege sie im Render‑Dashboard unter Service → Environment an."
    )

# --------------------------------------------------------------------
# 2. Create Engine
#    pool_pre_ping=True prevents idle timeouts in cloud deployments
# --------------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

# --------------------------------------------------------------------
# 3. Configure SessionFactory
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
# 5. Dependency for FastAPI endpoints
# --------------------------------------------------------------------
def get_db():
    """Yield‑based DB session for FastAPI Depends."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()