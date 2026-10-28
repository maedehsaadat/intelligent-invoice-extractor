import pandas as pd

def export_to_csv(records: list[dict]) -> bytes:
    """
    Convert extracted invoice records into a downloadable CSV file.
    """

    columns = [
        "invoice_number",
        "invoice_date",
        "vendor",
        "total_amount",
        "currency",
        "is_valid",
        "missing_fields",
        "warnings",
    ]

    dataframe = pd.DataFrame(records)

    # Ensure all expected columns exist and preserve their order.
    for column in columns:
        if column not in dataframe.columns:
            dataframe[column] = ""

    dataframe = dataframe[columns]

    # Convert list values to readable strings.
    for column in ["missing_fields", "warnings"]:
        dataframe[column] = dataframe[column].apply(
            lambda value: (
                "; ".join(str(item) for item in value)
                if isinstance(value, list)
                else value
            )
        )

    return dataframe.to_csv(
        index=False,
        encoding="utf-8-sig"
    ).encode("utf-8-sig")
