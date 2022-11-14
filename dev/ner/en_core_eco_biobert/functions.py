import spacy
from scispacy.custom_tokenizer import combined_rule_tokenizer
from spacy.training import Corpus, Example
from spacy.language import Language
from typing import Optional, Callable, Iterable, Iterator

@spacy.registry.callbacks("before_to_disk")
def create_callback():
    def before_to_disk(nlp):
        nlp.meta["name"] = "core_eco_weak_biobert"
        nlp.meta["version"] = "1.0.0"
        nlp.meta["description"] = "A full spaCy pipeline for ecological NER."
        nlp.meta["author"] = "Laboratoire d'Ecologie Alpine"
        nlp.meta["email"] = "nicolas.leguillarme@univ-grenoble-alpes.fr"
        nlp.meta["url"] = "https://github.com/nleguillarme/taxonerd"
        nlp.meta["labels"] = {"ner": ["LIVB"]}
        nlp.meta["license"] = "MIT"
        nlp.meta["pipeline"] = ["transformer", "tagger", "attribute_ruler", "lemmatizer", "parser", "ner"]
        return nlp

    return before_to_disk

@spacy.registry.callbacks("replace_tokenizer")
def replace_tokenizer_callback() -> Callable[[Language], Language]:
    def replace_tokenizer(nlp: Language) -> Language:
        nlp.tokenizer = combined_rule_tokenizer(nlp)
        #nlp.vocab = spacy.load("en_core_sci_md").vocab
        return nlp

    return replace_tokenizer
