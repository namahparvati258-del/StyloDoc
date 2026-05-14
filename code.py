import streamlit as st
import fitz  # PyMuPDF
import io
import pandas as pd
from PIL import Image

# Page Setup - StyloDoc Branding
st.set_page_config(page_title="StyloDoc - Smart PDF Workspace", layout="wide", page_icon="✒️")
st.title("✒️ StyloDoc: The Ultimate PDF Powerhouse")
st.write("Edit, Style, Merge, and Transform your PDFs with precision.")

# --- MULTI-FUNCTIONAL SIDEBAR ---
st.sidebar.header("🚀 StyloDoc Menu")
app_mode = st.sidebar.selectbox("Kya karna chahte hain?", 
                                 ["PDF Editor (Single File)", "PDF Merger (Multiple Files)"])

# ---------------------------------------------------------
# MODE 1: PDF MERGER
# ---------------------------------------------------------
if app_mode == "PDF Merger (Multiple Files)":
    st.header("🔗 PDF Merger: Do ya zyada PDF ko jodein")
    uploaded_files = st.file_uploader("PDF files select karein", type="pdf", accept_multiple_files=True)
    
    if uploaded_files and len(uploaded_files) >= 2:
        st.success(f"{len(uploaded_files)} files select ho gayi hain.")
        if st.button("Merge PDFs Now"):
            result_pdf = fitz.open()
            for uploaded_file in uploaded_files:
                file_bytes = uploaded_file.read()
                pdf_to_add = fitz.open(stream=file_bytes, filetype="pdf")
                result_pdf.insert_pdf(pdf_to_add)
            
            output = io.BytesIO()
            result_pdf.save(output)
            st.download_button("📥 Download Merged PDF", data=output.getvalue(), file_name="StyloDoc_Merged.pdf")
            result_pdf.close()
    else:
        st.info("Merge karne ke liye kam se kam 2 files upload karein.")

# ---------------------------------------------------------
# MODE 2: ADVANCED PDF EDITOR
# ---------------------------------------------------------
elif app_mode == "PDF Editor (Single File)":
    uploaded_file = st.file_uploader("Edit karne ke liye PDF upload karein", type="pdf")

    if uploaded_file:
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        st.sidebar.header("🛠️ StyloToolbox")
        page_num = st.sidebar.number_input("Page Number", min_value=1, max_value=len(doc), step=1) - 1
        
        edit_mode = st.sidebar.selectbox("Editing Tool select karein:", 
                                         ["Text (Write/Erase/Style)", "Image (Add/Resize)", "Table (Create New)", "Watermark (Security)"])

        # --- TEXT EDITING ---
        if edit_mode == "Text (Write/Erase/Style)":
            st.sidebar.subheader("📝 Text Styling")
            new_text = st.sidebar.text_area("Yahan apna text likhein:")
            font_size = st.sidebar.slider("Font Size", 8, 72, 12)
            font_color = st.sidebar.color_picker("Text Color", "#000000")
            is_underline = st.sidebar.checkbox("Underline")
            
            st.sidebar.subheader("📍 Position")
            tx = st.sidebar.slider("Left-Right (X)", 0, 600, 50)
            ty = st.sidebar.slider("Top-Bottom (Y)", 0, 800, 50)
            clear_area = st.sidebar.checkbox("Mitao (Erase) purana text?")

            if st.button("Apply Text Changes"):
                page = doc[page_num]
                rgb = tuple(int(font_color.lstrip('#')[i:i+2], 16) / 255 for (0, 2, 4))
                
                if clear_area:
                    rect = fitz.Rect(tx, ty - font_size, tx + (len(new_text) * font_size * 0.6), ty + 5)
                    page.add_redact_annot(rect, fill=(1, 1, 1)) 
                    page.apply_redactions()
                
                page.insert_text((tx, ty), new_text, fontsize=font_size, color=rgb, fontname="helv")
                
                if is_underline:
                    tw = fitz.get_text_length(new_text, fontsize=font_size)
                    page.draw_line(fitz.Point(tx, ty+2), fitz.Point(tx+tw, ty+2), color=rgb, width=1)
                st.success("StyloDoc has updated the text!")

        # --- IMAGE EDITING ---
        elif edit_mode == "Image (Add/Resize)":
            img_file = st.sidebar.file_uploader("Image upload karein", type=["png", "jpg", "jpeg"])
            if img_file:
                iw = st.sidebar.slider("Width", 20, 500, 150)
                ih = st.sidebar.slider("Height", 20, 500, 150)
                ix = st.sidebar.slider("X Position", 0, 600, 100)
                iy = st.sidebar.slider("Y Position", 0, 800, 100)
                if st.button("Add Image"):
                    page = doc[page_num]
                    page.insert_image(fitz.Rect(ix, iy, ix+iw, iy+ih), stream=img_file.read())
                    st.success("Image added by StyloDoc!")

        # --- TABLE CREATOR ---
        elif edit_mode == "Table (Create New)":
            rows = st.sidebar.number_input("Rows", 1, 10, 2)
            cols = st.sidebar.number_input("Cols", 1, 5, 2)
            st.write("### Table Data:")
            table_data = [[st.text_input(f"R{r+1}C{c+1}", key=f"r{r}c{c}") for c in range(cols)] for r in range(rows)]
            tx = st.sidebar.slider("Table X", 0, 600, 50)
            ty = st.sidebar.slider("Table Y", 0, 800, 200)
            
            if st.button("Generate Table"):
                page = doc[page_num]
                cw, ch = 100, 25
                for r in range(rows):
                    for c in range(cols):
                        rect = fitz.Rect(tx+c*cw, ty+r*ch, tx+(c+1)*cw, ty+(r+1)*ch)
                        page.draw_rect(rect, color=(0,0,0), width=1)
                        page.insert_text((tx+c*cw+5, ty+r*ch+18), str(table_data[r][c]), fontsize=10)
                st.success("Table generated!")

        # --- WATERMARK ---
        elif edit_mode == "Watermark (Security)":
            wm_text = st.sidebar.text_input("Watermark Text", "STYLO DOC")
            opac = st.sidebar.slider("Transparency", 0.1, 1.0, 0.3)
            if st.button("Apply to All Pages"):
                for page in doc:
                    page.insert_text((100, 400), wm_text, fontsize=70, 
                                     color=(0.7,0.7,0.7), fill_opacity=opac, rotate=45)
                st.success("StyloDoc Protection Applied!")

        # Save and Download
        out_pdf = io.BytesIO()
        doc.save(out_pdf)
        st.divider()
        st.download_button("📥 Download Final PDF", data=out_pdf.getvalue(), file_name="StyloDoc_Final.pdf")
        doc.close()