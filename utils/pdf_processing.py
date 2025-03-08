# utils/pdf_processing.py
import io
import pytesseract
from pdf2image import convert_from_bytes
from PyPDF2 import PdfReader
import streamlit as st

@st.cache_data(ttl=3600, show_spinner="Analyzing document content...")
def extract_text_with_ocr(pdf_content):
    """Unlimited hybrid text extraction with optimized OCR"""
    text = ""
    
    try:
        # First attempt: Full PDF text extraction
        with io.BytesIO(pdf_content) as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += f"{page_text}\n"
                    
        if text.strip():
            return text
            
    except Exception as e:
        st.warning(f"Standard extraction failed: {str(e)}")
    
    try:
        # Full OCR processing without page limits
        images = convert_from_bytes(
            pdf_content,
            dpi=300,  # Higher accuracy
            thread_count=8,
            fmt="png",  # Better for text
            use_pdftocairo=True,
            strict=False
        )
        
        # Process all pages with progress
        progress_bar = st.progress(0)
        for i, image in enumerate(images):
            text += f"\n[Page {i+1} OCR]\n"
            text += pytesseract.image_to_string(image) + "\n"
            progress_bar.progress((i+1)/len(images))
            
        return text
        
    except Exception as e:
        st.error(f"OCR failed: {str(e)}")
        return ""