from datetime import date, datetime
from math import isfinite


def validate_invoice_fields(fields: dict) -> dict:
    """
    Validate extracted invoice fields and return a validation summary.
    This checks basic consistency, not whether an invoice is authentic.
    """

    required_fields = [
        "invoice_number",
        "invoice_date",
        "vendor",
        "total_amount",
        "currency",
    ]

    missing_fields = []
    warnings = []

    # Check required fields
    for field in required_fields:
        value = fields.get(field)

        if value is None or (
            isinstance(value, str) and not value.strip()
        ):
            missing_fields.append(field)

    # Validate invoice date
    invoice_date = fields.get("invoice_date")

    if invoice_date and str(invoice_date).strip():
        parsed_date = None

        date_formats = (
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%m-%d-%Y",
            "%m/%d/%Y",
            "%d-%m-%y",
            "%d/%m/%y",
        )

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(
                    str(invoice_date).strip(), fmt
                ).date()
                break
            except ValueError:
                continue

        if parsed_date is None:
            warnings.append(
                "Invoice date format is not recognized."
            )
        elif parsed_date > date.today():
            warnings.append(
                "Invoice date is in the future."
            )

    # Validate total amount
    amount = fields.get("total_amount")

    # Skip validation when the amount is missing or empty
    if amount is not None and str(amount).strip() != "":
        try:
            amount = float(amount)

            if not isfinite(amount):
                warnings.append(
                    "Total amount must be a finite number."
                )
            elif amount < 0:
                warnings.append(
                    "Total amount cannot be negative."
                )

        except (TypeError, ValueError):
            warnings.append(
                "Total amount is not a valid number."
            )

    # Validate currency
    currency = fields.get("currency")

    supported_currencies = {
        "USD",
        "EUR",
        "GBP",
        "IRR",
        "AED",
    }

    if isinstance(currency, str) and currency.strip():
        if currency.strip().upper() not in supported_currencies:
            warnings.append(
                "Currency is not in the supported currency list."
            )

    # Return validation results
    return {
        "is_valid": (
            len(missing_fields) == 0
            and len(warnings) == 0
        ),
        "missing_fields": missing_fields,
        "warnings": warnings,
    }
