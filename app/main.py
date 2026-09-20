import streamlit as st
import os
import sys
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.extractor import extract_text
from src.parser import parse_document
from src.filler import fill_acroform, fill_scanned_form
from src.form_analyzer import get_form_fields, locate_form_fields
from app.theme import CUSTOM_CSS, icon, step_rail

MAX_FILE_SIZE_MB = 15
STEP_LABELS = ["Analyse", "Extraction", "Remplissage", "Téléchargement"]


def save_uploaded_file(uploaded_file, folder="tmp"):
    os.makedirs(folder, exist_ok=True)
    # 🔧 Ajout d'un UUID pour éviter les collisions de noms
    unique_name = f"{uuid.uuid4().hex}_{uploaded_file.name}"
    path = os.path.join(folder, unique_name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


def check_size(uploaded_file) -> bool:
    """Affiche une erreur et renvoie False si le fichier dépasse la limite autorisée."""
    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        st.markdown(
            f'{icon("warning", tone="stamp")} Fichier trop volumineux (max {MAX_FILE_SIZE_MB} Mo)',
            unsafe_allow_html=True,
        )
        return False
    st.markdown(f'{icon("check")} {uploaded_file.name} ({size_mb:.2f} Mo)', unsafe_allow_html=True)
    return True


st.set_page_config(page_title="Form Filling Agent", page_icon="🧾", layout="centered")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f'## {icon("form")} Form Filling Agent', unsafe_allow_html=True)
    st.markdown(
        "Remplit automatiquement un formulaire PDF à partir d'un document source, "
        "grâce à l'OCR et à Claude (Anthropic)."
    )
    st.markdown("**Comment ça marche ?**")
    st.markdown(
        f'{icon("document")} Déposez un document source<br><br>'
        f'{icon("form")} Déposez un formulaire PDF vierge<br><br>'
        f'{icon("search")} L\'app détecte les champs, extrait les données et remplit le formulaire<br><br>'
        f'{icon("download")} Téléchargez le résultat',
        unsafe_allow_html=True,
    )
    st.caption(f"Limite : {MAX_FILE_SIZE_MB} Mo par fichier")

st.markdown(f'# {icon("form")} Form Filling Agent', unsafe_allow_html=True)
st.caption("Remplissage automatique de formulaires PDF à partir d'un document source")

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown(f'#### {icon("document")} Document source', unsafe_allow_html=True)
    source = st.file_uploader(
        "Document source", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed"
    )
    source_ok = False
    if source:
        source_ok = check_size(source)
        if source_ok and source.type.startswith("image"):
            st.image(source, caption="Aperçu", use_container_width=True)

with col2:
    st.markdown(f'#### {icon("form")} Formulaire vierge', unsafe_allow_html=True)
    form = st.file_uploader("Formulaire vierge", type=["pdf"], label_visibility="collapsed")
    form_ok = False
    if form:
        form_ok = check_size(form)

st.divider()

if source and form and source_ok and form_ok:
    source_path = save_uploaded_file(source)
    form_path = save_uploaded_file(form)

    if st.button("Analyser et remplir", type="primary", use_container_width=True):
        rail = st.empty()
        rail.markdown(step_rail(STEP_LABELS, 0), unsafe_allow_html=True)

        # ── ÉTAPE 1/4 : détecter les champs du formulaire ──────────────────
        with st.status("Étape 1/4 — Analyse du formulaire", expanded=True) as status:
            acro_fields = get_form_fields(form_path)

            if acro_fields:
                form_fields = list(acro_fields.keys())
                use_acroform = True
                st.write(f"Formulaire interactif détecté — {len(form_fields)} champ(s) AcroForm")
            else:
                field_positions = locate_form_fields(form_path)  # fallback OCR (positions incluses)
                form_fields = sorted({pos["field"] for pos in field_positions})
                use_acroform = False
                st.write(f"Formulaire scanné — {len(form_fields)} champ(s) détecté(s) par OCR")

            st.write(", ".join(form_fields) if form_fields else "Aucun champ détecté")
            status.update(label="Étape 1/4 — Formulaire analysé", state="complete")
        rail.markdown(step_rail(STEP_LABELS, 1), unsafe_allow_html=True)

        # ── ÉTAPE 2/4 : extraire et mapper les données source ───────────────
        # Les st.expander ne peuvent pas être imbriqués dans un st.status
        # (lui-même un conteneur de type expander) : ils sont donc affichés
        # juste après, en frères et non en enfants du bloc de statut.
        with st.status("Étape 2/4 — Extraction des données", expanded=True) as status:
            text = extract_text(source_path)
            structured = parse_document(text, form_fields)  # champs réels du formulaire
            status.update(label="Étape 2/4 — Données extraites", state="complete")

        with st.expander("Texte extrait du document source"):
            st.markdown('<div class="ffa-mono">', unsafe_allow_html=True)
            st.text_area("Texte extrait", text, height=200, label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("Données extraites (JSON)"):
            st.json(structured)
        rail.markdown(step_rail(STEP_LABELS, 2), unsafe_allow_html=True)

        # ── ÉTAPE 3/4 : remplir le formulaire ──────────────────────────────
        with st.status("Étape 3/4 — Remplissage du formulaire", expanded=True) as status:
            output_path = form_path.replace(".pdf", "_filled.pdf")

            if use_acroform:
                fill_acroform(structured, form_path, output_path)  # form_path, pas source_path
            else:
                fill_scanned_form(structured, form_path, output_path)

            status.update(label="Étape 3/4 — Formulaire rempli", state="complete")
        rail.markdown(step_rail(STEP_LABELS, 3), unsafe_allow_html=True)

        # ── ÉTAPE 4/4 : téléchargement ──────────────────────────────────────
        st.markdown(
            f'{icon("check", tone="stamp")} **Formulaire rempli avec succès**', unsafe_allow_html=True
        )
        with open(output_path, "rb") as f:
            st.download_button(
                label="Télécharger le formulaire rempli",
                data=f,
                file_name="formulaire_rempli.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
        rail.markdown(step_rail(STEP_LABELS, 4), unsafe_allow_html=True)
else:
    st.markdown(
        f'{icon("search")} Déposez un document source et un formulaire vierge pour commencer',
        unsafe_allow_html=True,
    )
