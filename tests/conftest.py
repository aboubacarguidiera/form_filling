import pytest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


@pytest.fixture
def multi_page_acroform_pdf(tmp_path):
    """Builds a 2-page AcroForm PDF: 'nom' text field on page 1, 'prenom' on page 2."""
    pdf_path = tmp_path / "fixture.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)

    c.drawString(50, 750, "Page 1")
    c.acroForm.textfield(name="nom", tooltip="Nom", x=100, y=700, width=200, height=20)
    c.showPage()

    c.drawString(50, 750, "Page 2")
    c.acroForm.textfield(name="prenom", tooltip="Prenom", x=100, y=700, width=200, height=20)
    c.showPage()

    c.save()
    return str(pdf_path)


@pytest.fixture
def scanned_form_pdf(tmp_path):
    """Builds a 1-page non-AcroForm PDF with printed labels, standing in for a scanned form."""
    pdf_path = tmp_path / "scanned_form.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(72, 700, "Nom:")
    c.drawString(72, 650, "Date:")
    c.save()
    return str(pdf_path)
