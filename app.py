import hashlib
import html
import fitz
import pandas as pd
import streamlit as st
from src.pdf_extractor import extract_text_from_pdf
from src.ocr_extractor import extract_text_from_image
from src.field_extractor import extract_invoice_fields
from src.validator import validate_invoice_fields

# ==================================================
# Page configuration
# ==================================================

st.set_page_config(
    page_title="InvoiceAI | Invoice Data Extractor",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==================================================
# Session state
# ==================================================

DEFAULT_STATE = {
    "current_file_id": None,
    "invoice_fields": None,
    "extracted_text": None,
    "invoice_error": None,
    "invoice_error_details": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


DISPLAY_NAMES = {
    "invoice_number": "Invoice number",
    "invoice_date": "Invoice date",
    "vendor": "Vendor",
    "total_amount": "Total amount",
    "currency": "Currency",
}


# ==================================================
# Custom styling
# ==================================================

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    .stApp {
        background-color: #f5f7fb;
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        max-width: 1120px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .hero {
        background: linear-gradient(120deg, #14264b, #2458a6);
        padding: 2.2rem 2.4rem;
        border-radius: 22px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 12px 32px rgba(20, 38, 75, 0.14);
    }

    .hero-label {
        color: #bfdbfe;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.8px;
        margin-bottom: 0.8rem;
    }

    .hero h1 {
        color: white;
        font-size: 2.2rem;
        line-height: 1.2;
        font-weight: 800;
        margin: 0 0 0.8rem 0;
    }

    .hero p {
        color: #e0eaff;
        font-size: 1rem;
        line-height: 1.7;
        margin: 0;
        max-width: 720px;
    }

    .section-title {
        color: #172554;
        font-size: 1.25rem;
        font-weight: 750;
        margin-top: 1.5rem;
        margin-bottom: 0.3rem;
    }

    .section-description {
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 1rem 1.1rem;
        min-height: 108px;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.035);
    }

    .metric-label {
        color: #64748b;
        font-size: 0.8rem;
        margin-bottom: 0.6rem;
    }

    .metric-value {
        color: #172554;
        font-size: 1.15rem;
        font-weight: 750;
        overflow-wrap: anywhere;
    }

    .info-panel {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.2rem 1.3rem;
        margin: 0.8rem 0 1.2rem 0;
    }

    .footer-note {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        padding-top: 2rem;
    }

    div[data-testid="stFileUploader"] {
        background: white;
        border: 1px dashed #93aee0;
        border-radius: 16px;
        padding: 1rem;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        border-radius: 10px;
        font-weight: 650;
        min-height: 2.8rem;
    }

    div.stDownloadButton > button {
        background: #2458a6;
        color: white;
        border: 1px solid #2458a6;
    }

    div.stDownloadButton > button:hover {
        background: #193f7a;
        color: white;
        border-color: #193f7a;
    }

    div[data-testid="stTextInput"] input {
        border-radius: 9px;
        background-color: #ffffff;
    }

    @media (max-width: 700px) {
        .hero {
            padding: 1.5rem;
        }

        .hero h1 {
            font-size: 1.7rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# Header
# ==================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-label">AI-powered document processing</div>
        <h1>InvoiceAI</h1>
        <p>
            Extract important invoice information, validate the results,
            and export structured data in seconds.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-title">Upload your invoice</div>
    <div class="section-description">
        Supported formats: PDF, PNG, JPG, JPEG, TIF and TIFF.
        Scanned PDFs are processed using OCR.
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# PDF extraction with OCR fallback
# ==================================================

def extract_text_from_uploaded_pdf(pdf_bytes: bytes) -> str:
    """Extract selectable PDF text, with OCR fallback for scanned pages."""

    text = extract_text_from_pdf(pdf_bytes)

    if text and text.strip():
        return text.strip()

    page_texts = []

    with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
        for page in document:
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                alpha=False,
            )

            image_bytes = pixmap.tobytes("png")
            page_texts.append(extract_text_from_image(image_bytes))

    return "\n".join(page_texts).strip()


# ==================================================
# Helper functions
# ==================================================

def format_value(value):
    """Format values for the result summary cards."""

    if value is None or (
        isinstance(value, str) and not value.strip()
    ):
        return "Not detected"

    if isinstance(value, float):
        return f"{value:,.2f}"

    return str(value)


def reset_invoice_state(file_id):
    """Reset results and editing widgets when the uploaded file changes."""

    if st.session_state["current_file_id"] != file_id:
        st.session_state["current_file_id"] = file_id
        st.session_state["invoice_fields"] = None
        st.session_state["extracted_text"] = None
        st.session_state["invoice_error"] = None
        st.session_state["invoice_error_details"] = None

        for key in DISPLAY_NAMES:
            edit_key = f"edit_{key}"
            if edit_key in st.session_state:
                del st.session_state[edit_key]


# ==================================================
# Upload area
# ==================================================

uploaded_file = st.file_uploader(
    "Choose a file",
    type=["pdf", "png", "jpg", "jpeg", "tif", "tiff"],
    help="For best results, use a clear, readable invoice.",
)


if uploaded_file is None:
    st.session_state["current_file_id"] = None
    st.session_state["invoice_fields"] = None
    st.session_state["extracted_text"] = None
    st.session_state["invoice_error"] = None
    st.session_state["invoice_error_details"] = None

    for key in DISPLAY_NAMES:
        edit_key = f"edit_{key}"
        if edit_key in st.session_state:
            del st.session_state[edit_key]

    st.markdown(
        """
        <div class="info-panel">
            <strong style="color:#172554;">How it works</strong>
            <p style="color:#64748b; margin-bottom:0.4rem;">
                1. Upload a PDF or image of an invoice.
            </p>
            <p style="color:#64748b; margin-bottom:0.4rem;">
                2. Extract the invoice fields automatically.
            </p>
            <p style="color:#64748b; margin-bottom:0.4rem;">
                3. Review validation results and download a CSV file.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    file_bytes = uploaded_file.getvalue()
    filename = uploaded_file.name.lower()
    file_id = hashlib.md5(file_bytes).hexdigest()

    reset_invoice_state(file_id)

    st.markdown(
        f"""
        <div class="info-panel">
            <span style="color:#64748b; font-size:0.8rem;">
                SELECTED FILE
            </span>
            <div style="color:#172554; font-weight:700; margin-top:5px;">
                📄 {html.escape(uploaded_file.name)}
            </div>
            <div style="color:#64748b; font-size:0.8rem; margin-top:5px;">
                {len(file_bytes) / 1024:.1f} KB
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------
    # Extract button
    # --------------------------------------------------

    if st.button(
        "✨ Extract invoice information",
        type="primary",
        use_container_width=True,
    ):
        try:
            with st.spinner("Processing your invoice... This may take a moment."):
                if filename.endswith(".pdf"):
                    extracted_text = extract_text_from_uploaded_pdf(
                        file_bytes
                    )
                else:
                    extracted_text = extract_text_from_image(file_bytes)

                if not extracted_text.strip():
                    st.session_state["invoice_fields"] = None
                    st.session_state["extracted_text"] = None
                    st.session_state["invoice_error"] = (
                        "No text was detected. Try a clearer file "
                        "or check your OCR installation."
                    )
                else:
                    fields = extract_invoice_fields(extracted_text)

                    st.session_state["invoice_fields"] = fields
                    st.session_state["extracted_text"] = extracted_text
                    st.session_state["invoice_error"] = None
                    st.session_state["invoice_error_details"] = None

                    for key in DISPLAY_NAMES:
                        value = fields.get(key)
                        st.session_state[f"edit_{key}"] = (
                            "" if value is None else str(value)
                        )

        except Exception as exc:
            st.session_state["invoice_fields"] = None
            st.session_state["extracted_text"] = None
            st.session_state["invoice_error"] = (
                "Could not process this file. Check that it is a valid "
                "PDF or image and that OCR is installed if needed."
            )
            st.session_state["invoice_error_details"] = str(exc)

    # --------------------------------------------------
    # Processing errors
    # --------------------------------------------------

    if st.session_state.get("invoice_error"):
        st.warning(st.session_state["invoice_error"])

        if st.session_state.get("invoice_error_details"):
            with st.expander("Technical details"):
                st.code(st.session_state["invoice_error_details"])

    # --------------------------------------------------
    # Results
    # --------------------------------------------------

    fields = st.session_state.get("invoice_fields")
    extracted_text = st.session_state.get("extracted_text")

    if fields is not None and extracted_text is not None:
        st.markdown(
            """
            <div class="section-title">Extraction results</div>
            <div class="section-description">
                Review the extracted fields before using or exporting them.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Editable fields
        with st.expander("Review extracted fields", expanded=True):
            st.caption(
                "Review or correct the extracted values below. "
                "Validation and CSV export update automatically."
            )

            edited_fields = {}

            for key, label in DISPLAY_NAMES.items():
                edited_fields[key] = st.text_input(
                    label,
                    key=f"edit_{key}",
                    value=(
                        ""
                        if fields.get(key) is None
                        else str(fields.get(key))
                    ),
                )

        # Validate current edited values
        validation = validate_invoice_fields(edited_fields)

        # Summary cards
        card_fields = list(DISPLAY_NAMES.items())
        card_columns = st.columns(3)

        for index, (key, label) in enumerate(card_fields):
            value = format_value(edited_fields.get(key))

            with card_columns[index % 3]:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">
                            {html.escape(label)}
                        </div>
                        <div class="metric-value">
                            {html.escape(value)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Validation status
        if validation["is_valid"]:
            st.success("✓ Basic validation checks passed.")
        else:
            st.warning(
                "Some fields are missing or may need manual review."
            )

        with st.expander(
            "Validation details",
            expanded=not validation["is_valid"],
        ):
            if validation["missing_fields"]:
                st.markdown("**Missing fields**")
                for item in validation["missing_fields"]:
                    st.write(f"- {item}")
            else:
                st.write("No missing fields were reported.")

            if validation["warnings"]:
                st.markdown("**Warnings**")
                for warning in validation["warnings"]:
                    st.write(f"- {warning}")
            else:
                st.write("No validation warnings were reported.")

        # Extracted source text
        with st.expander("View extracted source text"):
            st.text(extracted_text)

        # --------------------------------------------------
        # CSV export
        # --------------------------------------------------

        st.markdown(
            """
            <div class="section-title">Export your data</div>
            <div class="section-description">
                Download the corrected fields and updated validation status as CSV.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Explicit column order and value mapping
        export_record = {
            "invoice_number": edited_fields.get("invoice_number", ""),
            "invoice_date": edited_fields.get("invoice_date", ""),
            "vendor": edited_fields.get("vendor", ""),
            "total_amount": edited_fields.get("total_amount", ""),
            "currency": edited_fields.get("currency", ""),
            "is_valid": str(validation["is_valid"]).upper(),
            "missing_fields": "; ".join(
                validation["missing_fields"]
            ),
            "warnings": "; ".join(
                validation["warnings"]
            ),
        }

        # Build the CSV directly with the expected columns.
        export_columns = [
            "invoice_number",
            "invoice_date",
            "vendor",
            "total_amount",
            "currency",
            "is_valid",
            "missing_fields",
            "warnings",
        ]

        export_dataframe = pd.DataFrame(
            [export_record],
            columns=export_columns,
        )

        csv_bytes = export_dataframe.to_csv(
            index=False,
            encoding="utf-8-sig",
        ).encode("utf-8-sig")

        st.download_button(
            label="⬇ Download results as CSV",
            data=csv_bytes,
            file_name="invoice_extraction.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_invoice_csv",
        )


# ==================================================
# Footer
# ==================================================

st.markdown(
    """
    <div class="footer-note">
        InvoiceAI · Intelligent Invoice Data Extractor
        <br>
        Prototype for document processing and data extraction.
        Always verify extracted information before business use.
    </div>
    """,
    unsafe_allow_html=True,
)
