"""The saved Word heading font must not be overridden by its theme."""

from pathlib import Path
from zipfile import ZipFile

import pytest
from defusedxml.ElementTree import fromstring

ROOT = Path(__file__).resolve().parents[1]
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = "{" + NS["w"] + "}"
DOCUMENTS = ["assets/neocam-document-styles.docx"]


@pytest.mark.parametrize("relative", DOCUMENTS)
def test_heading_font_is_explicit_times_new_roman(relative: str) -> None:
    """Reject theme overrides that select Calibri despite an explicit TNR name."""
    with ZipFile(ROOT / relative) as archive:
        styles = fromstring(archive.read("word/styles.xml"))
    for name in ("Heading1", "Heading2", "Heading3"):
        fonts = styles.find(f"w:style[@w:styleId='{name}']/w:rPr/w:rFonts", NS)
        assert fonts is not None, (relative, name)
        assert not any(key.casefold().endswith("theme") for key in fonts.attrib), (relative, name)
        assert all(fonts.get(W + script) == "Times New Roman" for script in ("ascii", "hAnsi", "eastAsia", "cs")), (
            relative,
            name,
        )


def test_reference_title_is_black_without_a_decorative_rule() -> None:
    """The reference cannot reintroduce a blue title or a title border."""
    with ZipFile(ROOT / DOCUMENTS[0]) as archive:
        styles = fromstring(archive.read("word/styles.xml"))
    title = styles.find("w:style[@w:styleId='Title']", NS)
    assert title is not None
    color = title.find("w:rPr/w:color", NS)
    assert color is not None
    assert color.attrib == {W + "val": "000000"}
    assert title.find("w:pPr/w:pBdr", NS) is None
