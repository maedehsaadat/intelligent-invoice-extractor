import re

def extract_invoice_fields(text: str) -> dict:
    """
    Extract common invoice fields from text using rule-based patterns.
    This is a baseline extractor, not a general-purpose AI model.
    """

    fields = {
        "invoice_number": None,
        "invoice_date": None,
        "vendor": None,
        "total_amount": None,
        "currency": None,
    }

    if not text or not text.strip():
        return fields

    text = text.replace("\r", "\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    normalized_text = "\n".join(lines)

    # 1. Invoice number
    match = re.search(
        r"(?im)\b(?:invoice\s*(?:number|no\.?|#)|inv\s*#)"
        r"\s*[:\-]?\s*([A-Z0-9][A-Z0-9\-\/]*)",
        normalized_text,
    )
    if match:
        fields["invoice_number"] = match.group(1).strip()

    # 2. Invoice date
    date_patterns = [
        r"(?im)\b(?:invoice\s*date|date)\s*[:\-]?\s*"
        r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b",
        r"(?im)\b(?:invoice\s*date|date)\s*[:\-]?\s*"
        r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b",
    ]

    for pattern in date_patterns:
        match = re.search(pattern, normalized_text)
        if match:
            fields["invoice_date"] = match.group(1).strip()
            break

    # 3. Vendor name
    excluded_patterns = [
        r"\binvoice\b",
        r"\bbill\s+to\b",
        r"\bship\s+to\b",
        r"\bdate\b",
        r"\btotal\b",
        r"\bdescription\b",
        r"\bamount\b",
        r"\bquantity\b",
        r"\bqty\b",
        r"\bprice\b",
        r"\bitem\b",
        r"\bgrand\s+total\b",
        r"\bsubtotal\b",
        r"\bcustomer\b",
        r"\bfor\s+testing\s+only\b",
    ]

    for line in lines[:10]:
        # Skip lines containing common invoice fields or table headings.
        if any(
            re.search(pattern, line, flags=re.IGNORECASE)
            for pattern in excluded_patterns
        ):
            continue

        # Skip lines that are primarily numeric or punctuation.
        if not re.search(r"[A-Za-z]", line):
            continue

        # Avoid treating long paragraphs as vendor names.
        if len(line) > 100:
            continue

        fields["vendor"] = line
        break

    # 4. Total amount and currency
    amount_pattern = (
        r"(?i)\b(?:grand\s+total|total\s+due|amount\s+due|total)\b"
        r"\s*[:\-]?\s*(USD|EUR|GBP|IRR|AED|\$|€|£)?\s*"
        r"(\d[\d,]*(?:\.\d{1,2})?)"
    )

    matches = list(re.finditer(amount_pattern, normalized_text))

    if matches:
        match = matches[-1]
        currency = match.group(1)
        amount = match.group(2).replace(",", "")

        fields["total_amount"] = float(amount)

        if currency:
            currency_map = {
                "$": "USD",
                "€": "EUR",
                "£": "GBP",
            }
            fields["currency"] = currency_map.get(
                currency, currency.upper()
            )

    return fields
