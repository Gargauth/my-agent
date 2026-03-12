"""Tesseract OCR wrapper — port of OCR.swift."""

from modules.errors import OcrFailed
from modules.models import OCRResult, UIElement


def recognize(image_path: str, min_confidence: float = 0.5) -> list[OCRResult]:
    """Run OCR on an image file. Returns list of text regions."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError as e:
        raise OcrFailed(f"Missing dependency: {e}. Install pytesseract and Pillow.")

    try:
        img = Image.open(image_path)
    except Exception as e:
        raise OcrFailed(f"Cannot load image: {e}")

    try:
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    except Exception as e:
        raise OcrFailed(str(e))

    results: list[OCRResult] = []
    n = len(data["text"])
    for i in range(n):
        text = data["text"][i].strip()
        if not text:
            continue
        conf = float(data["conf"][i])
        # Tesseract returns confidence as 0-100
        normalized_conf = conf / 100.0
        if normalized_conf < min_confidence:
            continue
        results.append(
            OCRResult(
                text=text,
                confidence=normalized_conf,
                x=int(data["left"][i]),
                y=int(data["top"][i]),
                width=int(data["width"][i]),
                height=int(data["height"][i]),
            )
        )
    return results


def to_elements(results: list[OCRResult]) -> list[UIElement]:
    """Convert OCR results to UIElements with O1, O2, ... IDs."""
    return [
        UIElement(
            id=f"O{i + 1}",
            role="ocrtext",
            label=r.text,
            x=r.x,
            y=r.y,
            width=r.width,
            height=r.height,
            is_enabled=True,
            depth=0,
        )
        for i, r in enumerate(results)
    ]
