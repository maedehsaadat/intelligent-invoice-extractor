# InvoiceAI — Intelligent Invoice Data Extractor

InvoiceAI is a Python-based application that extracts, validates, and exports invoice information from PDF documents and images.

## Features

- Extract text from PDF invoices.
- Use OCR to process image-based invoices.
- Extract key invoice fields, including invoice number, date, vendor, total amount, and currency.
- Validate extracted information and identify missing fields.
- Review and edit extracted values.
- Export invoice data to CSV for use in spreadsheet applications.
- Run automated tests for field extraction and validation.

## Tech Stack

- Python
- Streamlit
- PyMuPDF
- Tesseract OCR
- Pandas
- Pytest

## Project Structure

```text
intelligent-invoice-extractor/
├── app.py
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── pdf_extractor.py
│   ├── ocr_extractor.py
│   ├── field_extractor.py
│   ├── validator.py
│   └── exporter.py
└── tests/
    ├── test_field_extractor.py
    └── test_validator.py
```

## Installation

1. Clone the repository:

   ```bash
   git clone YOUR_REPOSITORY_URL
   cd intelligent-invoice-extractor
   ```

2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Install Tesseract OCR and ensure it is available to the application if OCR functionality is needed.

## Run the Application

```bash
streamlit run app.py
```

## Run Tests

```bash
python -m pytest
```

## Current Status

The application supports invoice data extraction, validation, editable field review, and CSV export. The current automated test suite contains six tests covering field extraction and validation.

## Limitations

Extraction accuracy may vary depending on invoice layout, image quality, OCR output, and date or number formats. Review extracted values before using them in business records.
