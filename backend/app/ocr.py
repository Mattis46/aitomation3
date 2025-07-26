"""Extended OCR processing for receipts.

This module builds upon the basic PDF parsing example provided in the
template repository.  It extracts structured data from German‐style
invoices.  In addition to the original fields (`date`, `net_amount`,
`tax_amount`, `gross_amount`, `supplier`), it now also provides
additional keys more aligned with the terminology used in the German
VAT pre‑declaration:

* ``invoice_date`` – the invoice date as a string in DD.MM.YYYY format
* ``vendor``       – the supplier name
* ``netto``        – the net amount (Decimal)
* ``umsatzsteuer`` – the VAT amount (Decimal)
* ``brutto``       – the gross amount (Decimal)
* ``steuersatz``   – the VAT rate in percent (int), ``None`` when
  the rate cannot be determined

The parsing strategy is intentionally simple and relies on regular
expressions to find dates and monetary amounts.  For production
systems you should use a dedicated OCR service (e.g. Mindee or
similar) that can reliably extract invoice numbers, line items and
tax rates.【866104154231912†L300-L304】【946044698870348†L60-L110】
"""

import logging
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional, Dict, Any

# Import pdfplumber lazily so that the module can be used even when
# the dependency is not installed in the execution environment (e.g.
# during unit testing).  When `pdfplumber` is missing a dummy object
# with an `open` method is substituted that raises an informative
# ImportError.  Unit tests can monkey‑patch this object to provide
# their own `open` implementation.
try:
    import pdfplumber  # type: ignore
except ImportError:
    class _DummyPdfplumber:
        def open(self, *_args, **_kwargs):  # type: ignore[no-untyped-def]
            raise ImportError(
                "pdfplumber is required to parse PDFs. "
                "Install it via `pip install pdfplumber` or monkey‑patch ``pdfplumber.open`` "
                "in tests."
            )

    pdfplumber = _DummyPdfplumber()  # type: ignore


# Regular expression for German date formats (e.g. 15.06.2025)
DATE_RE = re.compile(r"(\d{2}\.\d{2}\.\d{4})")
# Regular expression for monetary amounts (e.g. 1.234,56)
AMOUNT_RE = re.compile(r"([0-9]+(?:\.[0-9]{3})*,[0-9]{2})")


def _parse_amount(value: str) -> Optional[Decimal]:
    """Convert a German formatted number into a Decimal.

    The function replaces thousand separators (``.``) and comma
    separators (``","``) appropriately.  Returns ``None`` if the value
    cannot be parsed into a Decimal.

    Args:
        value: A string representing a monetary amount, e.g. "1.234,56".

    Returns:
        A ``Decimal`` or ``None`` if parsing fails.
    """
    cleaned = value.replace(".", "").replace(",", ".")
    try:
        return Decimal(cleaned)
    except (InvalidOperation, AttributeError):
        return None


def parse_receipt_pdf(file_path: str) -> Dict[str, Any]:
    """Parse a PDF receipt and return extracted invoice information.

    The parser looks through all pages of the given PDF and collects
    text lines.  It then uses simple heuristics to identify the
    invoice date, supplier name, monetary amounts and tax rate.  When
    multiple amounts are present, it assumes that the largest amount is
    the gross amount and tries to find two smaller amounts that sum to
    the gross amount (representing net and VAT amounts).  If no such
    combination is found, it falls back to returning only the largest
    amount as gross and leaving the other values ``None``.

    Args:
        file_path: Path to the PDF file on disk.

    Returns:
        A dictionary with the extracted data.  The dictionary always
        contains both the original keys (``date``, ``net_amount``,
        ``tax_amount``, ``gross_amount``, ``supplier``) for backward
        compatibility as well as the extended keys (``invoice_date``,
        ``vendor``, ``netto``, ``umsatzsteuer``, ``brutto``,
        ``steuersatz``).
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(file_path)

    date_str: Optional[str] = None
    net: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    gross: Optional[Decimal] = None
    supplier: Optional[str] = None

    # Read all pages and collect text lines
    text_lines: list[str] = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            if not supplier and lines:
                # heuristically use the first non‑empty line as supplier name
                supplier = lines[0]
            text_lines.extend(lines)
            # Look for date only once
            if not date_str:
                m = DATE_RE.search(text)
                if m:
                    date_str = m.group(1)
    # Join all lines into a single string for amount extraction
    full_text = " ".join(text_lines)
    amounts = AMOUNT_RE.findall(full_text)
    amounts_decimal = [_parse_amount(a) for a in amounts if _parse_amount(a) is not None]

    # Determine net, tax, gross using simple heuristics
    if amounts_decimal:
        # use unique sorted amounts to improve matching
        unique_amounts = sorted(set(amounts_decimal))
        gross_val = max(unique_amounts)
        gross = gross_val
        # Try to find two numbers that sum to the gross
        found = False
        for i in range(len(unique_amounts)):
            for j in range(i + 1, len(unique_amounts)):
                if abs(unique_amounts[i] + unique_amounts[j] - gross_val) < Decimal("0.05"):
                    # By convention the larger of the two matching amounts is the
                    # net amount and the smaller is the tax.  This heuristic
                    # reflects typical invoice layouts where net > tax.
                    a = unique_amounts[i]
                    b = unique_amounts[j]
                    net = max(a, b)
                    tax = min(a, b)
                    found = True
                    break
            if found:
                break
    # If amounts could not be matched, assign the single value to gross
    # and leave others as None

    # Determine tax rate when net and tax are available
    tax_rate: Optional[int] = None
    if net and tax and net != 0:
        try:
            ratio = (tax / net) * 100
            # round to nearest integer percentage
            rounded = int(ratio.quantize(Decimal("1")))
            # classify typical German VAT rates (19 % or 7 %)
            if 18 <= rounded <= 20:
                tax_rate = 19
            elif 6 <= rounded <= 8:
                tax_rate = 7
            else:
                tax_rate = rounded
        except Exception:
            tax_rate = None

    result: Dict[str, Any] = {
        # legacy keys used elsewhere in the codebase
        "date": date_str,
        "net_amount": net,
        "tax_amount": tax,
        "gross_amount": gross,
        "supplier": supplier,
        # extended keys for UStVA processing
        "invoice_date": date_str,
        "vendor": supplier,
        "netto": net,
        "umsatzsteuer": tax,
        "brutto": gross,
        "steuersatz": tax_rate,
    }

    # Log if extraction failed for any critical field
    for key in ["invoice_date", "netto", "umsatzsteuer", "brutto"]:
        if result[key] is None:
            logging.warning("OCR parsing could not extract %s from %s", key, file_path)
    return result