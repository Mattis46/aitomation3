"""Beispiel für die Beleg‑Verarbeitung (OCR).

Das Modul stellt Funktionen bereit, um Basisdaten aus PDF‑Dateien zu
extrahieren.  Es verwendet pdfplumber, ein Werkzeug zum Auslesen von
Text, Tabellen und Graphik‑Informationen aus PDFs【866104154231912†L300-L304】.  In
produktiven Systemen sollte ein spezialisiertes OCR‑Tool wie Mindee eingesetzt
werden, das Rechnungsfelder, Tabellenzeilen und Steuersätze zuverlässig
identifiziert【946044698870348†L60-L110】.
"""

import re
from decimal import Decimal
from pathlib import Path
from typing import Optional, Dict, Any

import pdfplumber


DATE_RE = re.compile(r"(\d{2}\.\d{2}\.\d{4})")
AMOUNT_RE = re.compile(r"([0-9]+,[0-9]{2})")


def parse_receipt_pdf(file_path: str) -> Dict[str, Any]:
    """Extrahiere Datum, Netto‑, Steuer‑ und Brutto‑Betrag sowie Lieferant aus einem PDF.

    Args:
        file_path: Pfad zur PDF‑Datei

    Returns:
        Ein Wörterbuch mit den extrahierten Informationen.  Nicht gefundene
        Werte sind ``None``.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(file_path)

    date: Optional[str] = None
    net: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    gross: Optional[Decimal] = None
    supplier: Optional[str] = None

    with pdfplumber.open(str(path)) as pdf:
        text_lines = []
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            text_lines.extend(lines)
            # Versuche Datum zu finden
            if not date:
                match = DATE_RE.search(text)
                if match:
                    date = match.group(1)
        # Suche Beträge in gesamtem Text
        all_text = " ".join(text_lines)
        amounts = AMOUNT_RE.findall(all_text)
        # Heuristik: Die höchsten drei Zahlen sind Brutto, Netto, USt
        if amounts:
            amounts_decimal = [Decimal(a.replace(",", ".")) for a in amounts]
            # Größte Zahl als Bruttobetrag
            gross_val = max(amounts_decimal)
            gross = gross_val
            # Netto + USt = Brutto
            # Suche zwei kleinere Beträge, die zusammen etwa dem Brutto entsprechen
            found = False
            for i in range(len(amounts_decimal)):
                for j in range(i + 1, len(amounts_decimal)):
                    if abs(amounts_decimal[i] + amounts_decimal[j] - gross_val) < Decimal("0.05"):
                        net = amounts_decimal[i]
                        tax = amounts_decimal[j]
                        found = True
                        break
                if found:
                    break
        # Lieferant: heuristisch erster Textblock
        if text_lines:
            supplier = text_lines[0]

    return {
        "date": date,
        "net_amount": net,
        "tax_amount": tax,
        "gross_amount": gross,
        "supplier": supplier,
    }