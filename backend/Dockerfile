# backend/Dockerfile
FROM python:3.11-slim

# System‑Abhängigkeiten (für pdfplumber / OCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis
WORKDIR /app

# ---------------- Install Python deps ----------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# -----------------------------------------------------

# Projektdateien
COPY app ./app

# Schnelleres Logging
ENV PYTHONUNBUFFERED=1

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
