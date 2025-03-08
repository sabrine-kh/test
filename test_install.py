import pytesseract
from pdf2image import convert_from_bytes

def test_ocr():
    try:
        print("Testing Tesseract...")
        print(pytesseract.get_tesseract_version())
        print("✓ Tesseract OK")
    except Exception as e:
        print(f"Tesseract error: {str(e)}")

def test_poppler():
    try:
        print("Testing Poppler...")
        convert_from_bytes(b"", poppler_path=r"C:\poppler-23-08-0\Library\bin")
        print("✓ Poppler OK")
    except Exception as e:
        print(f"Poppler error: {str(e)}")

if __name__ == "__main__":
    test_ocr()
    test_poppler()