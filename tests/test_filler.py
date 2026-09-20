import pypdf

from src.filler import fill_acroform


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
