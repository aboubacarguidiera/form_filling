import streamlit as st
import tempfile
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.extractor import extract_text
from src.parser import parse_document
from src.filler import fill_template

MAX_FILE_SIZE_MB = 15


def save_uploaded_file(uploaded_file, folder="tmp"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, uploaded_file.name)

    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    print("Le nom du fichier enregistré est :", path)

    return path


st.set_page_config(page_title="Form Filling Agent", page_icon="🧾", layout="centered")

st.title("🧾 Form Filling Agent")
st.caption("Automatic document → form filling")

source = st.file_uploader(
    "1) Source document (PDF / Image)",
    type=["pdf", "png", "jpg", "jpeg"]
)

form = st.file_uploader(
    "2) Blank form (PDF)",
    type=["pdf"]
)

if source:
    size_mb = source.size / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        st.error("Source file too large (max 15MB)")
        st.stop()

    st.success(f"Source uploaded ({size_mb:.2f} MB)")

    # Preview image
    if source.type.startswith("image"):

        st.image(source, caption="Source preview", use_column_width=True)

if form:
    size_mb = form.size / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        st.error("Form file too large (max 15MB)")
        st.stop()

    st.success(f"Form uploaded ({size_mb:.2f} MB)")


if source and form:

    source_path = save_uploaded_file(source)
    form_path = save_uploaded_file(form)

    st.info("📁 Files saved")

    if st.button("🔍 Extract text"):

        with st.spinner("Extracting text..."):
            text = extract_text(source_path)
            structured = parse_document(text)
            st.json(structured)
        print("La taille du texte")
        #print(len(text))
        st.success("Extraction done ✅")

        st.text_area("Extracted text", text, height=300)
        st.write("Form file path:", form_path)
        st.write("Structured data:", structured)
        fill_template(structured, source_path)
        st.success("Form filled ✅")