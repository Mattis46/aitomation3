"""Datenbankverbindung für das Buchhaltungssystem.

Dieses Modul richtet eine SQLAlchemy‑Engine und eine SessionFactory ein.
Die Verbindungsdaten werden über die Umgebungsvariable ``DATABASE_URL``
bezogen.  Bei Verwendung von Render oder Railway wird diese Variable in
der PaaS‑Konfiguration gesetzt.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Der Datenbank-URL muss das Schema ``postgresql+psycopg2://`` nutzen.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:pass@localhost:5432/accounting")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    """Dependency für FastAPI‑Routen zur Bereitstellung einer Datenbanksitzung."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()