import streamlit as st
import os
import sys
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.extractor import extract_text
from src.parser import parse_document
from src.filler import fill_acroform, fill_scanned_form
from src.form_analyzer import get_form_fields, get_form_fields_from_text 

MAX_FILE_SIZE_MB = 15


def save_uploaded_file(uploaded_file, folder="tmp"):
    os.makedirs(folder, exist_ok=True)
    # 🔧 Ajout d'un UUID pour éviter les collisions de noms
    unique_name = f"{uuid.uuid4().hex}_{uploaded_file.name}"
    path = os.path.join(folder, unique_name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


st.set_page_config(page_title="Form Filling Agent", page_icon="🧾", layout="centered")
st.title("🧾 Form Filling Agent")
st.caption("Automatic document → form filling")

source = st.file_uploader("1) Source document (PDF / Image)", type=["pdf", "png", "jpg", "jpeg"])
form = st.file_uploader("2) Blank form (PDF)", type=["pdf"])

if source:
    size_mb = source.size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        st.error("Source file too large (max 15MB)")
        st.stop()
    st.success(f"Source uploaded ({size_mb:.2f} MB)")
    if source.type.startswith("image"):
        st.image(source, caption="Source preview", use_container_width=True)  # 🔧 deprecated fix

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

    if st.button("🔍 Analyser et remplir"):

        # ── ÉTAPE 1 : détecter les champs du formulaire ──────────────────
        with st.spinner("Analyse du formulaire..."):
            acro_fields = get_form_fields(form_path)  # 🆕

            if acro_fields:
                form_fields = list(acro_fields.keys())
                use_acroform = True
                st.success(f"{len(form_fields)} champs AcroForm détectés")
            else:
                form_fields = get_form_fields_from_text(form_path)  # 🆕 fallback OCR
                use_acroform = False
                st.warning("Pas de champs interactifs — détection par OCR")

            st.write("Champs détectés :", form_fields)

        # ── ÉTAPE 2 : extraire et mapper les données source ───────────────
        with st.spinner("Extraction et mapping des données..."):
            text = extract_text(source_path)
            st.text_area("Texte extrait", text, height=200)

            structured = parse_document(text, form_fields)  # 🔧 on passe les champs réels
            st.json(structured)
            st.success("Extraction done ✅")

        # ── ÉTAPE 3 : remplir le formulaire ──────────────────────────────
        with st.spinner("Remplissage du formulaire..."):
            output_path = form_path.replace(".pdf", "_filled.pdf")

            if use_acroform:
                fill_acroform(structured, form_path, output_path)  # 🔧 form_path, pas source_path
                st.success("Formulaire rempli ✅")
            else:
                st.error("Formulaire scanné : positionnement automatique non encore supporté.")
                st.stop()

        # ── ÉTAPE 4 : téléchargement ──────────────────────────────────────
        with open(output_path, "rb") as f:
            st.download_button(          # 🆕 bouton de téléchargement
                label="📥 Télécharger le formulaire rempli",
                data=f,
                file_name="formulaire_rempli.pdf",
                mime="application/pdf"
            )