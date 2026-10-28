from src.field_extractor import extract_invoice_fields

def test_extract_invoice_fields():
    text = """
    ACME Supplies Ltd
    Invoice Number: INV-2026-104
    Invoice Date: 2026-10-20
    Total: USD 1,250.50
    """

    result = extract_invoice_fields(text)

    assert result["invoice_number"] == "INV-2026-104"
    assert result["invoice_date"] == "2026-10-20"
    assert result["vendor"] == "ACME Supplies Ltd"
    assert result["total_amount"] == 1250.50
    assert result["currency"] == "USD"


def test_empty_text_returns_empty_fields():
    result = extract_invoice_fields("")

    assert result == {
        "invoice_number": None,
        "invoice_date": None,
        "vendor": None,
        "total_amount": None,
        "currency": None,
    }
