# utils/pdf_processing.py
import io
import pytesseract
from pdf2image import convert_from_bytes
from PyPDF2 import PdfReader
import streamlit as st

@st.cache_data(ttl=3600, show_spinner="Analyzing document content...")
def extract_text_with_ocr(pdf_content):
    """Hybrid text extraction optimized for cloud deployment"""
    text = ""
    
    try:
        # First attempt: Fast PDF text extraction
        with io.BytesIO(pdf_content) as f:
            reader = PdfReader(f)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            
        if text.strip():  # More efficient empty check
            return text
            
    except Exception as e:
        st.warning(f"Standard extraction failed: {str(e)}")
    
    try:
        # OCR fallback with cloud-optimized settings
        images = convert_from_bytes(
            pdf_content,
            dpi=200,  # Reduced from default 300 for faster processing
            thread_count=4,
            fmt="jpeg"
        )
        
        # Process first 10 pages only to prevent timeouts
        for image in images[:10]:
            text += pytesseract.image_to_string(image) + "\n"
            
        return text
        
    except Exception as e:
        st.error(f"OCR failed: {str(e)}")
        return ""