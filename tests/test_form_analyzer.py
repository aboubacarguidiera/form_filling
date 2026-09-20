import pytest

from src.form_analyzer import locate_form_fields


def _fake_ocr_data(words):
    """Builds a pytesseract.image_to_data-shaped dict from a list of
    (text, conf, left, top, width, height, block_num, par_num, line_num)."""
    data = {
        "text": [], "conf": [], "left": [], "top": [], "width": [], "height": [],
        "block_num": [], "par_num": [], "line_num": [],
    }
    for text, conf, left, top, width, height, block_num, par_num, line_num in words:
        data["text"].append(text)
        data["conf"].append(conf)
        data["left"].append(left)
        data["top"].append(top)
        data["width"].append(width)
        data["height"].append(height)
        data["block_num"].append(block_num)
        data["par_num"].append(par_num)
        data["line_num"].append(line_num)
    return data


def test_locate_form_fields_converts_coordinates(monkeypatch, scanned_form_pdf):
    fake_data = _fake_ocr_data([
        ("Nom:", "95", 300, 345, 60, 30, 1, 1, 1),
        ("Date:", "94", 300, 545, 65, 30, 1, 1, 2),
    ])
    monkeypatch.setattr(
        "src.form_analyzer.pytesseract.image_to_data",
        lambda image, lang, output_type: fake_data,
    )

    positions = locate_form_fields(scanned_form_pdf, dpi=300)

    by_field = {pos["field"]: pos for pos in positions}
    assert set(by_field) == {"Nom", "Date"}
    assert by_field["Nom"]["page"] == 0
    assert by_field["Nom"]["x"] == pytest.approx(87.6)
    assert by_field["Nom"]["y"] == pytest.approx(702.0)
    assert by_field["Date"]["x"] == pytest.approx(88.8)
    assert by_field["Date"]["y"] == pytest.approx(654.0)


def test_locate_form_fields_skips_noise_no_colon_and_long_labels(monkeypatch, scanned_form_pdf):
    long_label = "A" * 35 + ":"
    fake_data = _fake_ocr_data([
        ("", "-1", 0, 0, 0, 0, 1, 1, 1),  # bloc/paragraphe, pas un mot
        ("Bonjour", "90", 10, 10, 50, 20, 1, 1, 2),
        ("tout", "90", 65, 10, 30, 20, 1, 1, 2),
        ("le", "90", 100, 10, 20, 20, 1, 1, 2),
        ("monde", "90", 125, 10, 40, 20, 1, 1, 2),  # ligne sans ":"
        (long_label, "92", 10, 40, 300, 20, 1, 1, 3),  # label >= 30 caractères
    ])
    monkeypatch.setattr(
        "src.form_analyzer.pytesseract.image_to_data",
        lambda image, lang, output_type: fake_data,
    )

    positions = locate_form_fields(scanned_form_pdf, dpi=300)

    assert positions == []
