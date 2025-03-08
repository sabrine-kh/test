import streamlit as st
import yaml
from pathlib import Path
from utils.pdf_processing import extract_text_with_ocr
from processors.material_filling import analyze as analyze_material_filling
from processors.pull_to_seat import analyze as analyze_pull_to_seat
import time

# Configuration
CONFIG_PATH = Path(__file__).parent / "config.yaml"
MAX_FILE_SIZE_MB = 50
ALLOWED_TYPES = ["application/pdf"]

def main():
    st.set_page_config(page_title="Material Analytics", layout="wide")
    
    # Header Section
    st.title("📄 Material Properties Analyzer")
    st.markdown("Upload technical documents to extract material attributes")
    
    # File Upload
    uploaded_files = st.file_uploader(
        "Drag & Drop PDF Files",
        type=["pdf"],
        accept_multiple_files=True,
        help=f"Max file size: {MAX_FILE_SIZE_MB}MB"
    )
    
    if uploaded_files:
        # Validate files
        valid_files = [
            f for f in uploaded_files 
            if f.type in ALLOWED_TYPES and f.size <= MAX_FILE_SIZE_MB*1024*1024
        ]
        
        with st.status("🔍 Processing documents...", expanded=True) as status:
            results = []
            
            for file in valid_files:
                try:
                    # File processing
                    st.write(f"📥 Processing {file.name}...")
                    start_time = time.time()
                    
                    # Text extraction
                    text = extract_text_with_ocr(file.read())
                    
                    # Attribute analysis
                    material = analyze_material_filling(text)
                    pull_seat = analyze_pull_to_seat(text)
                    
                    # Store results
                    results.append({
                        "filename": file.name,
                        "material_filling": material,
                        "pull_to_seat": pull_seat,
                        "processing_time": time.time() - start_time
                    })
                    
                    st.success(f"✅ {file.name} processed in {results[-1]['processing_time']:.1f}s")
                    
                except Exception as e:
                    st.error(f"❌ Error processing {file.name}: {str(e)}")
                    results.append({
                        "filename": file.name,
                        "error": str(e)
                    })
            
            status.update(label=f"Processed {len(valid_files)} files", state="complete")
        
        # Display Results
        st.subheader("📊 Analysis Results")
        
        # Summary Cards
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Files", len(valid_files))
        col2.metric("Successful Analyses", f"{sum(1 for r in results if 'error' not in r)}/{len(results)}")
        col3.metric("Avg Processing Time", f"{sum(r.get('processing_time',0) for r in results)/len(results):.1f}s")
        
        # Detailed Results
        for result in results:
            with st.expander(f"📄 {result['filename']}", expanded=False):
                if 'error' in result:
                    st.error(f"Processing error: {result['error']}")
                else:
                    cols = st.columns(2)
                    cols[0].markdown(f"""
                    **Material Filling**  
                    `{result['material_filling']}`
                    """)
                    cols[1].markdown(f"""
                    **Pull-to-Seat**  
                    `{result['pull_to_seat']}`
                    """)
                st.caption(f"Processing time: {result.get('processing_time',0):.2f} seconds")
        
        # Export Options
        st.download_button(
            label="📥 Export Results as CSV",
            data=convert_to_csv(results),
            file_name="material_analysis.csv",
            mime="text/csv"
        )

def convert_to_csv(results):
    """Convert results to CSV format"""
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)
    
    return output.getvalue()

if __name__ == "__main__":
    main()