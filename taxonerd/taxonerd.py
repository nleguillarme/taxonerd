import pandas as pd
import spacy
import os
from glob import glob
import warnings
import sys
import logging
from spacy import displacy
from spacy.tokens import Span
import torch

from scispacy.custom_sentence_segmenter import pysbd_sentencizer
from taxonerd.abbreviation import TaxonomicAbbreviationDetector
from taxonerd.extractor import TextExtractor


class TaxoNERD:
    def __init__(
        self,
        model="en_ner_eco_md",
        with_abbrev=False,
        with_linking=None,
        with_sentence=False,
        threshold=0.7,
        prefer_gpu=False,
        verbose=False,
        logger=None,
    ):
        self.logger = logger if logger else logging.getLogger(__name__)
        warnings.simplefilter("ignore")

        self.verbose = verbose
        self.extractor = TextExtractor(logger=self.logger)
        if prefer_gpu:
            use_cuda = torch.cuda.is_available()
            self.logger.info("GPU is available" if use_cuda else "GPU not found")
            if use_cuda:
                spacy.require_gpu()
                self.logger.info("TaxoNERD will use GPU")
        self.logger.info("Load model {}".format(model))
        self.nlp = spacy.load(model)
        self.logger.info(
            "Loaded model {}-{}".format(self.nlp.meta["name"], self.nlp.meta["version"])
        )

        self.with_sentence = with_sentence
        if self.with_sentence:
            if self.verbose:
                self.logger.info(f"Add pySBDSentencizer to pipeline")
                if not Span.has_extension("sent_id"):
                    Span.set_extension("sent_id", default=None)
            self.nlp.add_pipe("pysbd_sentencizer", before="ner")

        self.with_abbrev = with_abbrev
        if self.with_abbrev:
            if self.verbose:
                self.logger.info(f"Add TaxonomicAbbreviationDetector to pipeline")
            self.nlp.add_pipe("taxonomic_abbreviation_detector")

        self.with_linking = with_linking != None
        if self.with_linking:
            kb_name = with_linking if with_linking != "" else "gbif_backbone"
            if self.verbose:
                self.logger.info(f"Add EntityLinker {kb_name} to pipeline")
            self.create_linker(kb_name, threshold)

    def create_linker(self, kb_name, threshold):
        from taxonerd.linking.linking_utils import KnowledgeBaseFactory
        from taxonerd.linking.candidate_generation import CandidateGenerator
        from taxonerd.linking.linking import EntityLinker

        self.nlp.add_pipe(
            "taxonerd_linker",
            config={
                "linker_name": kb_name,
                "resolve_abbreviations": self.with_abbrev,
                "filter_for_definitions": False,
                "k": 1,
                "threshold": threshold,
            },
        )

    def find_in_corpus(self, input_dir, output_dir=None):
        df_map = {}
        input_dir = self.extractor(input_dir)
        if input_dir:
            for filename in glob(os.path.join(input_dir, "*.txt")):
                df = self.find_in_file(filename, output_dir)
                if df is not None:
                    df_map[os.path.basename(filename)] = df
        return df_map

    def find_in_file(self, filename, output_dir=None):
        if not os.path.exists(filename):
            raise FileNotFoundError("File {} not found".format(path))
        filename = self.extractor(filename)
        if filename:
            self.logger.info("Extract taxa from file {}".format(filename))
            with open(filename, "r") as f:
                text = f.read()
            df = self.find_in_text(text)
            if output_dir:
                ann_filename = os.path.join(
                    output_dir,
                    ".".join(os.path.basename(filename).split(".")[:-1]) + ".ann",
                )
                df.to_csv(ann_filename, sep="\t", header=False)
                return ann_filename
            return df
        return None

    def find_in_text(self, text):
        doc = self.ner(text)
        return self.doc_to_df(doc)

    def ner(self, text):
        def is_valid_entity(ent, doc, text):
            return (
                "\n" not in text[ent.start_char : ent.end_char].strip("\n")
                and (ent.label_ in ["LIVB", "TAXON"])
                and (ent._.kb_ents if self.with_linking else True)
                and ((ent not in doc._.abbreviations) if self.with_abbrev else True)
            )

        def is_valid_abbrev(abrv, ents_dict):
            return (
                abrv._.long_form
                and abrv.text != abrv._.long_form.text
                and abrv._.long_form.text in ents_dict
            )

        doc = self.nlp(text)
        # displacy.serve(doc, style="ent")

        ents = []
        if len(doc.ents) > 0:
            # Keep only the entities that have been linked
            if self.with_linking:
                ents += [ent for ent in doc.ents if is_valid_entity(ent, doc, text)]
                doc.set_ents(ents)

        if len(doc.ents) > 0:
            ents = [ent for ent in doc.ents]
            # Keep only abbreviations whose long forms have been tagged as entities
            if self.with_abbrev and len(doc._.abbreviations) > 0:
                ents_dict = {ent.text: ent for ent in doc.ents}
                abbreviations = [
                    abrv
                    for abrv in doc._.abbreviations
                    if is_valid_abbrev(abrv, ents_dict)
                ]

                # scispacy's AbbreviationDetector may return overlapping spans -> keep the longest
                keep_abbrev = [True] * len(abbreviations)
                for i in range(len(abbreviations)):
                    if keep_abbrev[i]:
                        for j in range(i + 1, len(abbreviations)):
                            abrv_i = abbreviations[i]
                            abrv_j = abbreviations[j]
                            if not (
                                abrv_i.start > abrv_j.end or abrv_i.end < abrv_j.start
                            ):  # Overlapping
                                if len(abrv_i) <= len(abrv_j):
                                    keep_abbrev[i] = False
                                    self.logger.debug(
                                        f"Remove abbreviation ({abrv_i}, {abrv_i.start}, {abrv_i.end}) included in ({abrv_j}, {abrv_j.start}, {abrv_j.end})"
                                    )
                                else:
                                    keep_abbrev[j] = False
                                    self.logger.debug(
                                        f"Remove abbreviation ({abrv_j}, {abrv_j.start}, {abrv_j.end}) included in ({abrv_i}, {abrv_i.start}, {abrv_i.end})"
                                    )

                # Abbreviations may overlap with entities -> remove them
                for i in range(len(abbreviations)):
                    if keep_abbrev[i]:
                        overlapping_span = False
                        abrv = abbreviations[i]
                        for ent in doc.ents:
                            if not (
                                ent.start > abrv.end or ent.end < abrv.start
                            ):  # Overlapping
                                self.logger.debug(
                                    f"Remove abbreviation ({abrv}, {abrv.start}, {abrv.end}) included in ({ent}, {ent.start}, {ent.end})"
                                )
                                overlapping_span = True
                                break
                        if not overlapping_span:
                            new_ent = Span(doc, abrv.start, abrv.end, "LIVB")
                            if self.with_linking:
                                new_ent._.kb_ents = ents_dict[
                                    abrv._.long_form.text
                                ]._.kb_ents
                            ents.append(new_ent)

                doc.set_ents(ents)

        if len(doc.ents) > 0:
            # Add the sentence id as an entity attribute
            if self.with_sentence:
                sentences = {sent: id for id, sent in enumerate(doc.sents)}
                for ent in doc.ents:
                    ent._.sent_id = sentences[ent.sent]

        return doc

    def doc_to_df(self, doc):
        def get_entity_dict(ent):
            ent_dict = {
                "offsets": "LIVB {} {}".format(ent.start_char, ent.end_char),
                "text": ent.text.replace("\n", " "),
            }
            if self.with_linking:
                ent_dict["entity"] = ent._.kb_ents
            if self.with_sentence:
                ent_dict["sent"] = ent._.sent_id
            return ent_dict

        entities = []
        if len(doc.ents) > 0:
            entities = [get_entity_dict(ent) for ent in doc.ents]
        df = pd.DataFrame(entities)
        df = df.dropna()
        df = df.loc[df.astype(str).drop_duplicates().index]
        df = df.reset_index(drop=True)
        return df.rename("T{}".format)
