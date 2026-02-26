import pypdf
# remplir un pdf interactif (acroform) avec les données extraites et parsées
from pypdf.generic import NameObject, create_string_object
from reportlab.pdfgen import canvas     
from reportlab.lib.pagesizes import letter
def fill_acroform(parsed_data: dict, form_path: str, output_path: str):
    reader = pypdf.PdfReader(form_path)
    writer = pypdf.PdfWriter()
    writer.append(reader)
    
    writer.update_page_form_field_values(
        writer.pages[0], 
        {k: str(v) for k, v in parsed_data.items() if v is not None}
    )
    with open(output_path, "wb") as f:
        writer.write(f)

# remplir un pdf scanné (non interactif) en créant une nouvelle page avec les données extraites

def fill_scanned_form(parsed_data: dict, form_path: str, output_path: str):
    c = canvas.Canvas(output_path, pagesize=letter)
    c.drawString(100, 750, "Formulaire rempli automatiquement")
    y = 700
    for field, value in parsed_data.items():
        c.drawString(100, y, f"{field}: {value}")
        y -= 30
    c.save()
