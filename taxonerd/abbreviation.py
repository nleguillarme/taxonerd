from scispacy.abbreviation import AbbreviationDetector

from typing import Tuple, List, Optional, Set, Dict
from collections import defaultdict
from spacy.tokens import Span, Doc
from spacy.matcher import Matcher
from spacy.language import Language
from itertools import compress
import re


@Language.factory("taxo_abbrev_detector")
class TaxonomicAbbreviationDetector(AbbreviationDetector):
    def __init__(
        self,
        nlp: Language,
        name: str = "taxo_abbrev_detector",
    ) -> None:
        Doc.set_extension("abbreviations", default=[], force=True)
        Span.set_extension("long_form", default=None, force=True)

        AbbreviationDetector.__init__(self, nlp, name)

    def __call__(self, doc: Doc) -> Doc:
        doc = super().__call__(doc)
        doc = self.apply_filter(doc)
        doc = self.find_abbreviated_scientific_names(doc)
        return doc

    def find_abbreviated_scientific_names(self, doc):
        """
        Match abbreviated scientific names with their long form.
        """

        def is_abbreviated_scientific_name(span, abb_name_pattern):
            return len(span) > 1 and abb_name_pattern.fullmatch(span[0].text)

        def is_long_form_of_abbreviated_name(span, abb):
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

        abb_name_pattern = re.compile("[A-Z]{1}\.")
        ents = []
        short_to_long_map = {}
        for short_candidate in doc.ents:
            if (
                short_candidate.text not in short_to_long_map
                and is_abbreviated_scientific_name(short_candidate, abb_name_pattern)
            ):
                long_forms = set(
                    [
                        span
                        for span in doc.ents
                        if is_long_form_of_abbreviated_name(span, short_candidate)
                    ]
                )
                short_to_long_map[short_candidate.text] = (
                    next(iter(long_forms)) if long_forms else None
                )  # What if several matches for long form ?

            if short_candidate.text in short_to_long_map:
                short_candidate._.long_form = short_to_long_map[short_candidate.text]
            else:
                short_candidate._.long_form = short_candidate
            ents.append(short_candidate)
        doc.set_ents(ents)
        return doc

    def apply_filter(self, doc):
        """
        Keep only abbreviations whose long forms match taxonomic entities.
        """

        def is_valid_abbrev(abrv, ents_dict):
            return (
                abrv._.long_form
                and abrv.text != abrv._.long_form.text
                and abrv._.long_form.text in ents_dict
            )

        def remove_overlapping_spans(spans):
            keep = [True] * len(spans)
            for i in range(len(spans)):
                if keep[i]:
                    for j in range(i + 1, len(spans)):
                        span_i = spans[i]
                        span_j = spans[j]
                        if not (
                            span_i.start > span_j.end or span_i.end < span_j.start
                        ):  # Overlapping, keep the longest span
                            if len(span_i) <= len(span_j):
                                keep[i] = False
                            else:
                                keep[j] = False
            return list(compress(spans, keep))

        ents = [ent for ent in doc.ents]
        if ents and len(doc._.abbreviations) > 0:
            ents_dict = {ent.text: ent for ent in ents}
            abbreviations = [
                abrv for abrv in doc._.abbreviations if is_valid_abbrev(abrv, ents_dict)
            ]
            # scispacy's AbbreviationDetector may return overlapping spans -> keep the longest
            abbreviations = remove_overlapping_spans(abbreviations)
            # Abbreviations may overlap with entities -> remove them
            for i in range(len(abbreviations)):
                overlapping_span = False
                abrv = abbreviations[i]
                for ent in doc.ents:
                    if not (ent.start > abrv.end or ent.end < abrv.start):
                        overlapping_span = True
                        break  # Current abbreviation overlaps an entity. Stop.
                if not overlapping_span:
                    new_ent = Span(doc, abrv.start, abrv.end, "LIVB")
                    new_ent._.long_form = abrv._.long_form
                    ents.append(new_ent)
            doc.set_ents(ents)
        return doc
