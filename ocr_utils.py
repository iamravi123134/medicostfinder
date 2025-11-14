from PIL import Image
import pytesseract
import os

def ocr_image_to_text(image_path):
    """
    Returns extracted text from an image file using pytesseract.
    Supports common image types. For PDFs, you should pre-convert pages to images.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError("image not found")

    img = Image.open(image_path).convert("RGB")
    # Basic pre-processing could be added here (resize, thresholding)
    text = pytesseract.image_to_string(img, lang='eng')
    # Normalize whitespace
    text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
    return text