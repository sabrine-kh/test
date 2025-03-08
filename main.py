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
    st.set_page_config(
        page_title="Material Analytics",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header Section
    st.title("📄 Combined Document Analyzer")
    st.markdown("Upload multiple technical documents for combined analysis")
    
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
            combined_text = ""
            processing_times = []
            
            try:
                # First pass: Combine all text
                for file in valid_files:
                    st.write(f"📥 Extracting text from {file.name}...")
                    start_time = time.time()
                    
                    # Extract and combine text
                    file_content = file.read()
                    text = extract_text_with_ocr(file_content)
                    combined_text += f"\n----- {file.name} -----\n{text}"
                    
                    processing_time = time.time() - start_time
                    processing_times.append(processing_time)
                    st.success(f"✅ {file.name} processed in {processing_time:.1f}s")
                
                # Second pass: Analyze combined text
                st.write("🔍 Analyzing combined content...")
                analysis_start = time.time()
                
                material = analyze_material_filling(combined_text)
                pull_seat = analyze_pull_to_seat(combined_text)
                
                total_analysis_time = time.time() - analysis_start
                processing_times.append(total_analysis_time)
                
                status.update(label=f"Processed {len(valid_files)} files", state="complete")
                
            except Exception as e:
                st.error(f"❌ Processing failed: {str(e)}")
                return
            
        # Display Results
        st.subheader("📊 Combined Analysis Results")
        
        # Summary Cards
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Files", len(valid_files))
        col2.metric("Total Processing Time", f"{sum(processing_times):.1f}s")
        col3.metric("Analysis Time", f"{total_analysis_time:.1f}s")
        
        # Combined Results
        st.markdown("### Material Attributes")
        cols = st.columns(2)
        cols[0].markdown(f"""
        **Material Filling**  
        `{material}`
        """)
        cols[1].markdown(f"""
        **Pull-to-Seat**  
        `{pull_seat}`
        """)
        
        # Source Documents
        with st.expander("📚 Processed Documents"):
            for file in valid_files:
                st.caption(f"📄 {file.name}")
        
        # Export Options
        csv_data = convert_to_csv({
            "material_filling": material,
            "pull_to_seat": pull_seat,
            "processed_files": [f.name for f in valid_files]
        })
        
        st.download_button(
            label="📥 Export Results as CSV",
            data=csv_data,
            file_name="combined_analysis.csv",
            mime="text/csv"
        )

def convert_to_csv(results):
    """Convert results to CSV format"""
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Attribute", "Value"])
    writer.writerow(["Material Filling", results["material_filling"]])
    writer.writerow(["Pull-to-Seat", results["pull_to_seat"]])
    writer.writerow([])
    writer.writerow(["Processed Files"] + results["processed_files"])
    
    return output.getvalue()

if __name__ == "__main__":
    main()