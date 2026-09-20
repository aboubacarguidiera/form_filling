# pour un pdf interacftif (acroform)
import pdfplumber
import pypdf
import pytesseract

def get_form_fields(form_path: str) -> dict:
    reader = pypdf.PdfReader(form_path)
    fields = reader.get_fields()
    if not fields:
        return {}
    # Retourne {nom_du_champ: valeur_actuelle (vide)}
    return {k: v.get("/V", "") for k, v in fields.items()}


def _group_words_into_lines(ocr_data: dict) -> list[list[dict]]:
    # Regroupe les mots pytesseract (image_to_data) par ligne détectée,
    # en ignorant le texte vide et les tokens sans confiance (conf < 0,
    # ce sont des marqueurs de bloc/paragraphe, pas des mots).
    lines: dict[tuple[int, int, int], list[dict]] = {}
    order: list[tuple[int, int, int]] = []
    for i, text in enumerate(ocr_data["text"]):
        text = text.strip()
        conf = float(ocr_data["conf"][i])
        if not text or conf < 0:
            continue
        key = (ocr_data["block_num"][i], ocr_data["par_num"][i], ocr_data["line_num"][i])
        word = {
            "text": text,
            "left": ocr_data["left"][i],
            "top": ocr_data["top"][i],
            "width": ocr_data["width"][i],
            "height": ocr_data["height"][i],
        }
        if key not in lines:
            lines[key] = []
            order.append(key)
        lines[key].append(word)
    return [lines[key] for key in order]


def _extract_label_anchor(line_words: list[dict], max_label_len: int = 30):
    # Même heuristique que l'ancienne détection texte : label = ce qui précède
    # le premier ":". L'ancre est le mot contenant ":" (son bord droit indique
    # où écrire la valeur).
    line_text = " ".join(w["text"] for w in line_words)
    if ":" not in line_text:
        return None
    label = line_text.split(":")[0].strip()
    if not label or len(label) >= max_label_len:
        return None
    anchor_word = next((w for w in line_words if ":" in w["text"]), line_words[-1])
    return label, anchor_word


LABEL_VALUE_GAP_PT = 5  # espace visuel label -> valeur, en points PDF (indépendant du dpi)
LABEL_VALUE_Y_LIFT_PT = 3  # décale la valeur au-dessus du trait imprimé, au lieu d'écrire dessus


def locate_form_fields(form_path: str, dpi: int = 300) -> list[dict]:
    # Détecte par OCR les champs d'un formulaire scanné (non-AcroForm) et
    # renvoie leur position en points PDF, pour superposer les valeurs
    # au bon endroit sur le PDF source (voir fill_scanned_form).
    scale = 72.0 / dpi
    results = []
    with pdfplumber.open(form_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            image = page.to_image(resolution=dpi).original
            ocr_data = pytesseract.image_to_data(
                image, lang="eng+fra", output_type=pytesseract.Output.DICT
            )
            for line_words in _group_words_into_lines(ocr_data):
                extracted = _extract_label_anchor(line_words)
                if extracted is None:
                    continue
                label, anchor = extracted
                x_pt = (anchor["left"] + anchor["width"]) * scale + LABEL_VALUE_GAP_PT
                y_pt = page.height - (anchor["top"] + anchor["height"]) * scale + LABEL_VALUE_Y_LIFT_PT
                results.append({"field": label, "page": page_index, "x": x_pt, "y": y_pt})
    return results