import io

import pypdf
# remplir un pdf interactif (acroform) avec les données extraites et parsées
from pypdf.generic import NameObject, create_string_object
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from src.form_analyzer import locate_form_fields

def fill_acroform(parsed_data: dict, form_path: str, output_path: str):
    reader = pypdf.PdfReader(form_path)
    writer = pypdf.PdfWriter()
    writer.append(reader)
    
    writer.update_page_form_field_values(
        None,
        {k: str(v) for k, v in parsed_data.items() if v is not None}
    )
    writer.set_need_appearances_writer(True)
    with open(output_path, "wb") as f:
        writer.write(f)

# remplir un pdf scanné (non interactif) en superposant les valeurs sur le PDF source,
# aux positions détectées par OCR (voir locate_form_fields)

def fill_scanned_form(parsed_data: dict, form_path: str, output_path: str):
    positions_by_page: dict[int, list[dict]] = {}
    for pos in locate_form_fields(form_path):
        positions_by_page.setdefault(pos["page"], []).append(pos)

    reader = pypdf.PdfReader(form_path)
    writer = pypdf.PdfWriter()

    for page_index, page in enumerate(reader.pages):
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=(float(page.mediabox.width), float(page.mediabox.height)))
        for pos in positions_by_page.get(page_index, []):
            value = parsed_data.get(pos["field"])
            if value is not None:
                c.drawString(pos["x"], pos["y"], str(value))
        c.save()
        buf.seek(0)
        page.merge_page(pypdf.PdfReader(buf).pages[0])
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)
