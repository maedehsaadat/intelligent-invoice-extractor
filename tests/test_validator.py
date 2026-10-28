from src.validator import validate_invoice_fields

def test_valid_invoice_fields():
    fields = {
        "invoice_number": "INV-1001",
        "invoice_date": "2026-10-20",
        "vendor": "ACME Supplies Ltd",
        "total_amount": 1250.50,
        "currency": "USD",
    }

    result = validate_invoice_fields(fields)

    assert result["is_valid"] is True
    assert result["missing_fields"] == []
    assert result["warnings"] == []


def test_missing_invoice_number():
    fields = {
        "invoice_number": None,
        "invoice_date": "2026-10-20",
        "vendor": "ACME Supplies Ltd",
        "total_amount": 1250.50,
        "currency": "USD",
    }

    result = validate_invoice_fields(fields)

    assert result["is_valid"] is False
    assert "invoice_number" in result["missing_fields"]


def test_negative_total_amount():
    fields = {
        "invoice_number": "INV-1002",
        "invoice_date": "2026-10-20",
        "vendor": "ACME Supplies Ltd",
        "total_amount": -50,
        "currency": "USD",
    }

    result = validate_invoice_fields(fields)

    assert result["is_valid"] is False
    assert any(
        "negative" in warning.lower()
        for warning in result["warnings"]
    )


def test_invalid_date_format():
    fields = {
        "invoice_number": "INV-1003",
        "invoice_date": "not-a-date",
        "vendor": "ACME Supplies Ltd",
        "total_amount": 100,
        "currency": "USD",
    }

    result = validate_invoice_fields(fields)

    assert result["is_valid"] is False
    assert any(
        "date format" in warning.lower()
        for warning in result["warnings"]
    )
