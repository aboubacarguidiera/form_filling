import shutil

import pdfplumber
import pypdf
import pytest

from src.filler import fill_acroform, fill_scanned_form


def test_fill_acroform_fills_fields_on_all_pages(multi_page_acroform_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")

    fill_acroform({"nom": "Dupont", "prenom": "Jean"}, multi_page_acroform_pdf, output_path)

    fields = pypdf.PdfReader(output_path).get_fields()
    assert fields["nom"]["/V"] == "Dupont"
    assert fields["prenom"]["/V"] == "Jean"


def test_fill_acroform_sets_need_appearances(multi_page_acroform_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")

    fill_acroform({"nom": "Dupont", "prenom": "Jean"}, multi_page_acroform_pdf, output_path)

    acro_form = pypdf.PdfReader(output_path).trailer["/Root"]["/AcroForm"]
    assert bool(acro_form["/NeedAppearances"])


def test_fill_acroform_skips_none_values_across_pages(multi_page_acroform_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")

    fill_acroform({"nom": "Dupont", "prenom": None}, multi_page_acroform_pdf, output_path)

    fields = pypdf.PdfReader(output_path).get_fields()
    assert fields["nom"]["/V"] == "Dupont"
    assert fields["prenom"]["/V"] == ""


def _fake_scanned_positions():
    return [
        {"field": "Nom", "page": 0, "x": 150, "y": 700},
        {"field": "Date", "page": 0, "x": 150, "y": 650},
    ]


def test_fill_scanned_form_overlays_values_and_preserves_original_content(
    monkeypatch, scanned_form_pdf, tmp_path
):
    monkeypatch.setattr(
        "src.filler.locate_form_fields", lambda form_path: _fake_scanned_positions()
    )
    output_path = str(tmp_path / "output.pdf")

    fill_scanned_form({"Nom": "Dupont", "Date": "2024-01-01"}, scanned_form_pdf, output_path)

    reader = pypdf.PdfReader(output_path)
    assert len(reader.pages) == 1

    with pdfplumber.open(output_path) as pdf:
        text = pdf.pages[0].extract_text()
    assert "Dupont" in text
    assert "2024-01-01" in text
    assert "Nom:" in text
    assert "Date:" in text


def test_fill_scanned_form_skips_missing_values(monkeypatch, scanned_form_pdf, tmp_path):
    monkeypatch.setattr(
        "src.filler.locate_form_fields", lambda form_path: _fake_scanned_positions()
    )
    output_path = str(tmp_path / "output.pdf")

    fill_scanned_form({"Nom": "Dupont", "Date": None}, scanned_form_pdf, output_path)

    with pdfplumber.open(output_path) as pdf:
        text = pdf.pages[0].extract_text()
    assert "Dupont" in text
    assert "2024-01-01" not in text


@pytest.mark.skipif(shutil.which("tesseract") is None, reason="tesseract binary not installed")
def test_fill_scanned_form_end_to_end_real_ocr(scanned_form_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")

    fill_scanned_form({"Nom": "Dupont", "Date": "2024-01-01"}, scanned_form_pdf, output_path)

    with pdfplumber.open(output_path) as pdf:
        text = pdf.pages[0].extract_text()
    assert "Dupont" in text
    assert "2024-01-01" in text


def test_fill_scanned_form_matches_value_despite_key_mismatch(
    monkeypatch, scanned_form_pdf, tmp_path
):
    # Le LLM peut renvoyer une clé légèrement différente du label OCR d'origine
    # (ex. il corrige "Né(e} le" -- accolade mal reconnue par l'OCR -- en
    # "Né(e) le"). La correspondance normalisée doit quand même retrouver la
    # valeur au lieu de la perdre silencieusement.
    monkeypatch.setattr(
        "src.filler.locate_form_fields",
        lambda form_path: [{"field": "Né(e} le", "page": 0, "x": 150, "y": 700}],
    )
    output_path = str(tmp_path / "output.pdf")

    fill_scanned_form({"Né(e) le": "03/11/1985"}, scanned_form_pdf, output_path)

    with pdfplumber.open(output_path) as pdf:
        text = pdf.pages[0].extract_text()
    assert "03/11/1985" in text
