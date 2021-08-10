from scispacy.abbreviation import AbbreviationDetector

from typing import Tuple, List, Optional, Set, Dict
from collections import defaultdict
from spacy.tokens import Span, Doc
from spacy.matcher import Matcher
from spacy.language import Language

import re


@Language.factory("taxonomic_abbreviation_detector")
class TaxonomicAbbreviationDetector(AbbreviationDetector):
    def __init__(
        self,
        nlp: Language,
        name: str = "taxonomic_abbreviation_detector",
    ) -> None:
        Doc.set_extension("abbreviations", default=[], force=True)
        Span.set_extension("long_form", default=None, force=True)

        AbbreviationDetector.__init__(self, nlp, name)
        self.abb_name_pattern = re.compile("[A-Z]{1}\.")

    def __call__(self, doc: Doc) -> Doc:
        doc = super().__call__(doc)
        doc = self.find_abbreviated_scientific_names(doc)
        return doc

    def find_abbreviated_scientific_names(self, doc):
        short_to_long_map = {}
        for short_candidate in doc.ents:
            if (
                short_candidate.text not in short_to_long_map
                and self.is_abbreviated_scientific_name(short_candidate)
            ):
                long_forms = set(
                    [
                        span
                        for span in doc.ents
                        if self.is_long_form_of_abbreviated_name(span, short_candidate)
                    ]
                )
                if long_forms:
                    long_form = next(
                        iter(long_forms)
                    )  # What if several matches for long form ?
                    short_to_long_map[short_candidate.text] = long_form

                else:
                    short_to_long_map[short_candidate.text] = None

            if short_candidate.text in short_to_long_map:
                short_candidate._.long_form = short_to_long_map[short_candidate.text]
                doc._.abbreviations.append(short_candidate)
                # print(short_candidate.text, short_candidate._.long_form)
        return doc

    def is_abbreviated_scientific_name(self, span):
        return len(span) > 1 and self.abb_name_pattern.fullmatch(span[0].text)

    def is_long_form_of_abbreviated_name(self, span, abb):
        if (
            (span.text != abb.text)
            and (len(span) == len(abb))
            and (span[0].text[0] == abb[0].text[0])
            and span.end < abb.start
        ):
            for i in range(1, len(span)):
                if span[i].text != abb[i].text:
                    return False
            return True
        return False
