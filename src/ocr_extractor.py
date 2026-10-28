from io import BytesIO
import pytesseract
from PIL import Image, ImageOps, ImageEnhance, ImageFilter


# Path to the installed Tesseract OCR engine
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extract text from an invoice image using Tesseract OCR.

    Tries multiple page segmentation modes and selects the result
    containing the most recognized text.
    """
    try:
        with Image.open(BytesIO(image_bytes)) as original_image:
            image = ImageOps.exif_transpose(original_image)
            image = image.convert("RGB")

            # Enlarge the image to improve OCR accuracy.
            if image.width < 1600:
                scale = 1600 / image.width
                new_size = (
                    1600,
                    int(image.height * scale)
                )
                image = image.resize(new_size, Image.Resampling.LANCZOS)

            # Create an enhanced grayscale version.
            grayscale = ImageOps.grayscale(image)
            grayscale = ImageEnhance.Contrast(grayscale).enhance(1.5)
            grayscale = grayscale.filter(ImageFilter.SHARPEN)

            # Try multiple OCR configurations on both versions.
            candidates = []

            for processed_image in (image, grayscale):
                for psm in (6, 4, 3):
                    text = pytesseract.image_to_string(
                        processed_image,
                        lang="eng",
                        config=f"--oem 3 --psm {psm}"
                    ).strip()

                    if text:
                        candidates.append(text)

            if not candidates:
                return ""

            # Select the result containing the most non-whitespace characters.
            return max(
                candidates,
                key=lambda result: len("".join(result.split()))
            )

    except Exception as exc:
        raise ValueError(
            "Could not process this image. Check the image file "
            "and OCR installation."
        ) from exc
