import io
import pytesseract
from pdf2image import convert_from_bytes
from PyPDF2 import PdfReader
import streamlit as st

@st.cache_data(ttl=3600)
def extract_text_with_ocr(pdf_content):
    """Hybrid text extraction with OCR fallback"""
    text = ""
    
    try:
        # First attempt: Standard PDF text extraction
        with io.BytesIO(pdf_content) as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += f"{page_text}\n"
        if len(text.strip()) > 50:  # Simple validity check
            return text
    except Exception as e:
        st.warning(f"Standard extraction failed: {str(e)}")
    
    try:
        # Fallback to OCR
        images = convert_from_bytes(pdf_content)
        for image in images:
            text += pytesseract.image_to_string(image) + "\n"
        return text
    except Exception as e:
        st.error(f"OCR failed: {str(e)}")
        return ""