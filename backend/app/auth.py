"""
Firebase‑basierte Authentifizierungsfunktionen.

Dieses Modul initialisiert die Firebase‑Admin‑SDK mit dem im
Environment hinterlegten Service‑Account und bietet eine FastAPI
Dependency zum Verifizieren von ID‑Tokens aus dem Authorization‑Header.
"""

import json
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

# -----------------------------------------------------------------------
# Firebase‑Admin initialisieren
# -----------------------------------------------------------------------
# Die Service‑Account‑JSON wird als Umgebungsvariable gespeichert.
# Sie kann als JSON‑String oder Pfad zu einer JSON‑Datei angegeben werden.
service_account_json = os.getenv("SERVICE_ACCOUNT_JSON")
if not service_account_json:
    raise RuntimeError(
        "SERVICE_ACCOUNT_JSON ist nicht gesetzt. "
        "Hinterlege die JSON des Firebase‑Service‑Accounts als Secret im Render‑Dashboard."
    )

# Wenn die Variable wie eine Datei aussieht, den Inhalt lesen,
# andernfalls davon ausgehen, dass es sich um einen JSON‑String handelt.
try:
    if service_account_json.strip().startswith("{"):
        cred_data = json.loads(service_account_json)
    else:
        with open(service_account_json, "r", encoding="utf-8") as f:
            cred_data = json.load(f)
except Exception as exc:
    raise RuntimeError(f"Kann SERVICE_ACCOUNT_JSON nicht lesen: {exc}") from exc

# Nur initialisieren, wenn es noch keine Firebase‑App gibt.
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_data)
    firebase_admin.initialize_app(cred)

# OAuth2PasswordBearer liest das Bearer‑Token aus dem Authorization‑Header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Validiert ein Firebase ID‑Token und gibt den dekodierten Inhalt zurück.

    Wird das Token nicht gefunden oder ist es ungültig/abgelaufen,
    wird eine HTTP 401‑Exception ausgelöst.
    """
    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiges oder abgelaufenes Token",
            headers={"WWW-Authenticate": "Bearer"},
        )