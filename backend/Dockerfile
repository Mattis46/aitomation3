FROM python:3.11-slim

# Arbeitsverzeichnis anlegen
WORKDIR /app

# Systemabhängigkeiten installieren
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    poppler-utils \
 && rm -rf /var/lib/apt/lists/*

# Abhängigkeiten installieren
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Anwendung kopieren
COPY backend/app ./app

# Port festlegen
EXPOSE 8000

# Standard‑Befehl
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]