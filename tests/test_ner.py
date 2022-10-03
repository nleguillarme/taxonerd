import pytest
from taxonerd import TaxoNERD


@pytest.fixture
def taxonerd():
    taxonerd = TaxoNERD()
    exclude = []
    taxonerd.load(model="en_core_eco_md", exclude=exclude, linker="taxref")
    return taxonerd


@pytest.fixture
def text_with_entities():
    return open("./tests/test_data/test_txt/test1.txt", "r").read()


@pytest.fixture
def pdf_with_entities():
    return "./tests/test_data/test_pdf/test.pdf"


@pytest.fixture
def jpg_with_entities():
    return "./tests/test_data/test_jpg/test.jpg"


@pytest.fixture
def text_wo_entities():
    return """Software test fixtures initialize test functions.
        They provide a fixed baseline so that tests execute reliably
        and produce consistent, repeatable, results.
        Initialization may setup services, state, or other operating
        environments."""


@pytest.fixture
def empty_text():
    return ""


def test_ner_with_entities(taxonerd, text_with_entities):
    doc = taxonerd.ner(text_with_entities)
    assert doc != None
    assert len(doc.ents) > 0


def test_ner_without_entities(taxonerd, text_wo_entities):
    doc = taxonerd.ner(text_wo_entities)
    assert doc != None
    assert len(doc.ents) == 0


def test_ner_with_empty_text(taxonerd, empty_text):
    doc = taxonerd.ner(empty_text)
    assert doc != None
    assert len(doc.ents) == 0


def test_pdf_with_entities(taxonerd, pdf_with_entities):
    df = taxonerd.find_in_file(pdf_with_entities)
    assert df.shape[0] > 0


def test_jpg_with_entities(taxonerd, jpg_with_entities):
    df = taxonerd.find_in_file(jpg_with_entities)
    assert df.shape[0] > 0
