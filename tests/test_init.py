import pytest
from taxonerd import TaxoNERD


def test_init_wo_gpu():
    taxonerd = TaxoNERD()
    assert taxonerd != None


def test_init_with_gpu():
    taxonerd = TaxoNERD(prefer_gpu=True)
    assert taxonerd != None


def test_load_minimal():
    taxonerd = TaxoNERD()
    exclude = [
        "tagger",
        "attribute_ruler",
        "lemmatizer",
        "parser",
        "pysbd_sentencizer",
        "taxo_abbrev_detector",
    ]
    taxonerd.load(model="en_core_eco_md", exclude=exclude)
    assert taxonerd.nlp != None
    assert taxonerd.nlp.pipe_names == ["tok2vec", "ner"]


def test_load_full():
    taxonerd = TaxoNERD()
    exclude = []
    taxonerd.load(model="en_core_eco_md", exclude=exclude)
    assert taxonerd.nlp != None
    assert taxonerd.nlp.pipe_names == [
        "tok2vec",
        "tagger",
        "attribute_ruler",
        "lemmatizer",
        "pysbd_sentencizer",
        "parser",
        "ner",
        "taxo_abbrev_detector",
    ]


def test_load_linker():
    taxonerd = TaxoNERD()
    exclude = [
        "tagger",
        "attribute_ruler",
        "lemmatizer",
        "parser",
        "pysbd_sentencizer",
        "taxo_abbrev_detector",
    ]
    taxonerd.load(model="en_core_eco_md", exclude=exclude, linker="taxref")
    assert taxonerd.nlp != None
    assert taxonerd.nlp.pipe_names == [
        "tok2vec",
        "ner",
        "taxref_linker",
    ]
