# Cloud-basiertes Buchhaltungssystem für KMU

Dieses Repository enthält ein Beispiel‑Projekt für ein cloudbasiertes Buchhaltungs‑SaaS.  Das System besteht aus einem **React/Tailwind‑Frontend** und einem **FastAPI‑Backend**.  Es soll kleinen und mittleren Unternehmen ermöglichen, Belege hochzuladen, Umsatzsteuervoranmeldungen (UStVA) zu berechnen und offene Posten automatisch zu erinnern.  Die Infrastruktur ist so entworfen, dass sie auf einer Plattform‑as‑a‑Service wie Render, Railway oder Fly.io deployt werden kann.

## Architekturübersicht

Das System gliedert sich in drei Komponenten:

1. **Frontend** – Eine moderne Single‑Page‑Application auf Basis von React und Tailwind CSS.  Nutzer können sich anmelden (z. B. über Firebase Authentication oder Auth0), Belege als PDF oder Foto hochladen und ihr Dashboard einsehen.  Firebase Authentication unterstützt mehrere Login‑Methoden (E‑Mail/Passwort, Telefon, Google, Facebook, GitHub) und bietet u. a. Multi‑Factor‑Authentication, Passwort‑Reset‑Funktionen und eine sichere Token‑Übertragung【788687444698245†L107-L127】.  Als Alternative zu Firebase kann Auth0 verwendet werden, das u. a. Single‑Sign‑On, verschiedene Login‑Optionen (soziale Logins, passwortlos via OTP, biometrisch), Multi‑Factor‑Authentication mit SMS, Push‑Benachrichtigungen, WebAuthn und Passwort‑Sicherheitsprüfungen bietet【648042238215115†L236-L352】.  Beide Dienste lassen sich einfach in React integrieren.

2. **Backend** – Eine FastAPI‑Anwendung mit REST‑Endpunkten für Kunden, Belege, UStVA‑Berechnungen und offene Posten.  Belege werden mithilfe von OCR verarbeitet.  Als Beispiel wird [pdfplumber](https://github.com/jsvine/pdfplumber) verwendet, das Text, Tabellen und geometrische Informationen aus PDFs extrahieren kann【866104154231912†L300-L304】.  Alternativ kann ein spezialisierter OCR‑Dienst wie Mindee eingesetzt werden, der Rechnungsnummern, Datum, Beträge, Steuersätze und Zeilenpositionen automatisch erkennt【946044698870348†L60-L110】.

3. **Datenhaltung & Services** – PostgreSQL dient als relationale Datenbank, S3/Google‑Cloud‑Storage als Objektspeicher für hochgeladene Dateien.  Amazon S3 speichert Dateien mit hoher Haltbarkeit ("11 Neunen") und unbegrenzter Skalierbarkeit【793146188439800†L110-L137】.  E‑Mails (u. a. Zahlungserinnerungen) können über Mailjet versendet werden.  Mailjet v3.1 verlangt in jeder Nachricht die Angabe von Absender‐ und Empfängerfeldern sowie den Text- oder HTML‑Inhalt【202248353458367†L68-L96】.

> **Hinweis:** Diese Repository‑Struktur ist ein Ausgangspunkt und dient der Illustration.  Die Implementierungen sind bewusst einfach gehalten.  Für einen produktiven Einsatz müssen Tests, Fehlerbehandlung, umfassende Validierung und Sicherheitsaspekte ergänzt werden.

## Verzeichnisstruktur

```
accounting-saas/
├── backend/                    # FastAPI‑Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # Einstiegspunkt für Uvicorn
│   │   ├── database.py        # SQLAlchemy‑Datenbankverbindung
│   │   ├── models.py          # SQLAlchemy‑Modelle
│   │   ├── schemas.py         # Pydantic‑Schemas für API
│   │   ├── api.py             # API‑Routen (CRUD)
│   │   ├── ocr.py             # Beispiel für Beleg‑Parsing
│   │   └── scheduler.py       # Reminder‑Scheduler (APScheduler)
│   ├── requirements.txt       # Python‑Abhängigkeiten
│   └── Dockerfile            # Image für das Backend
├── frontend/                   # React/Tailwind‑Frontend
│   ├── package.json           # npm‑Abhängigkeiten
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   └── Login.jsx
│       └── components/
│           ├── ReceiptUpload.jsx
│           ├── ReceiptList.jsx
│           ├── UstvaStatus.jsx
│           └── OpenItems.jsx
├── render.yaml                 # Beispiel‑Konfiguration für Render‑Deployment
└── README.md                   # Diese Datei
```

## Setup und lokale Ausführung

### Voraussetzungen

* **Docker** – Für lokale Entwicklung und Deployment.
* **Node 14+ und npm** – Für das Frontend.
* **Python 3.10+** – Wenn das Backend lokal ohne Docker ausgeführt wird.

### Backend

1. Wechseln Sie in das Backend‑Verzeichnis:

   ```bash
   cd backend
   ```

2. Erstellen Sie ein virtuelles Environment (optional) und installieren Sie die Abhängigkeiten:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Starten Sie das Backend lokal:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Besuchen Sie http://localhost:8000/docs, um die automatisch generierte OpenAPI‑Dokumentation zu sehen.

### Frontend

1. Wechseln Sie in das Frontend‑Verzeichnis:

   ```bash
   cd frontend
   ```

2. Installieren Sie die Abhängigkeiten:

   ```bash
   npm install
   ```

3. Starten Sie den lokalen Entwicklungsserver (Vite):

   ```bash
   npm run dev
   ```

4. Die Anwendung ist unter http://localhost:5173 erreichbar.

## Deployment auf Render.com

Dieses Projekt enthält eine Beispiel‑`render.yaml`.  Laut der Render‑Dokumentation muss die Blueprint‑Datei **render.yaml** im Wurzelverzeichnis liegen und beschreibt Services, Datenbanken und Umgebungsgruppen【432159069719870†L190-L299】.  Render erkennt die Datei automatisch beim Push in das Repository und legt entsprechende Services an.

Die enthaltene Blueprint definiert zwei Services:

1. **web (Frontend)** – Baut das React‑Projekt und dient die statischen Dateien über Render’s Static Site Service.
2. **api (Backend)** – Baut das Docker‑Image für das FastAPI‑Backend und startet `uvicorn`.  Die Umgebungsvariablen wie `DATABASE_URL`, `S3_BUCKET` und API‑Keys werden über Render‑Secrets konfiguriert.

Um zu deployen:

1. Erstellen Sie ein neues Repository bei GitHub und pushen Sie den Code.
2. Melden Sie sich bei render.com an und klicken Sie auf **New Blueprint**.  Render liest das `render.yaml`, erstellt die Services und fragt nach den erforderlichen Secrets (z. B. Datenbank‑URL, Mailjet‑Key).
3. Nach jeder Änderung im Repository wird automatisch ein Build gestartet (CI/CD).  Änderungen an der `render.yaml` führen zu aktualisierten Services【432159069719870†L190-L299】.

## Datenmodelle

Die wichtigsten Datenobjekte der Anwendung sind als SQLAlchemy‑Modelle implementiert (`backend/app/models.py`).  Für die API werden zusätzlich Pydantic‑Schemas (`backend/app/schemas.py`) genutzt.

| Modell    | Felder (Auswahl) | Beschreibung |
|----------|------------------|--------------|
| **Customer** | `id`, `name`, `email`, `vat_id` | Kunde, dem Belege zugeordnet werden. |
| **Receipt**  | `id`, `customer_id`, `file_path`, `date`, `net_amount`, `tax_amount`, `gross_amount`, `supplier` | Ein hochgeladener Beleg (Rechnung).  Die Beträge und das Datum werden durch OCR aus der Datei extrahiert. |
| **Ustva**    | `id`, `customer_id`, `period` (Jahr/Monat), `tax_sum`, `net_sum`, `gross_sum`, `generated_at` | Ergebnis der monatlichen Umsatzsteuervoranmeldung mit Summen der Netto‑ und Steuerbeträge. |
| **OpenItem** | `id`, `customer_id`, `description`, `amount`, `due_date`, `paid` | Offene Posten (z. B. Kundenforderungen).  Diese Posten werden vom System überwacht, und es werden Zahlungserinnerungen versendet. |

Weitere Details finden Sie in `backend/app/models.py`.

## OCR‑Beispiel

In `backend/app/ocr.py` befindet sich ein Beispiel für die Belegverarbeitung.  Mithilfe von [pdfplumber](https://github.com/jsvine/pdfplumber) werden Text und Tabellen aus PDF‑Dateien extrahiert.  pdfplumber kann einzelne Zeichen, Tabellen und Linien aus PDFs auslesen【866104154231912†L300-L304】.  Anschließend sucht die Funktion mit regulären Ausdrücken nach Datum, Netto‑ und Bruttobeträgen sowie der Umsatzsteuer.  Für komplexe Rechnungen kann ein externer Dienst wie Mindee Invoice OCR eingesetzt werden, der Rechnungsnummern, Beträge, Steuersätze und Tabellendaten automatisch erkennt【946044698870348†L60-L110】.

## Scheduler‑Beispiel

Der Reminder‑Scheduler (`backend/app/scheduler.py`) verwendet APScheduler mit einem Cron‑Trigger.  Der Scheduler führt zwei Aufgaben aus:

1. **Missing Receipts Reminder** – Am fünften Tag des Monats wird geprüft, ob ein Kunde im Vormonat Belege hochgeladen hat.  Falls nicht, sendet das System eine freundliche Erinnerung per E‑Mail.
2. **Payment Reminder** – Täglich überprüft der Scheduler offene Posten.  Bei überfälligen Rechnungen wird eine Zahlungserinnerung an die hinterlegte Adresse versendet.  Der Versand erfolgt über Mailjet unter Nutzung der v3.1 API, welche Absender‑ und Empfängerfelder sowie einen Text‑ oder HTML‑Part erfordert【202248353458367†L68-L96】.

Die Scheduler‑Jobs laufen in einem separaten Thread beim Starten der Anwendung.  Bei Deployment auf Render kann stattdessen ein **Background Worker** definiert werden.

## Sicherheit und Erweiterung

* **Authentifizierung** – Die Beispielanwendung ist offen und muss mit einem Auth‑Provider gesichert werden.  Firebase Authentication bietet u. a. verschiedene Auth‑Methoden, sichere Token‑Übertragung und Multi‑Factor‑Authentication【788687444698245†L107-L127】.  Auth0 erweitert dies um Single‑Sign‑On, passwortlose Logins, Biometrie und anpassbare Login‑Oberflächen【648042238215115†L236-L344】.
* **E‑Mail‑Versand** – Mailjet muss mit einem API‑Key und Secret konfiguriert werden; diese sollten als Secrets in der Deploy‑Plattform hinterlegt werden.
* **Datei‑Speicher** – Für den produktiven Einsatz sollte ein Cloud‑Speicher (z. B. AWS S3) genutzt werden.  S3 bietet unbegrenzten Speicher und eine Verfügbarkeit von 99.999999999 % (elf Neunen)【793146188439800†L110-L137】.

## Weiterentwicklung

Diese Vorlage kann erweitert werden, um weitere Funktionen wie GoBD‑konforme Archivierung, DATEV‑Export, Anbindung an Banking‑APIs oder eine B2B‑Rechnungsstellung (ZUGFeRD/XRechnung) zu implementieren.  Die modulare Struktur erleichtert die Anpassung an individuelle Anforderungen von Steuerberatern und Mandanten.