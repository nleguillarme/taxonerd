import pandas as pd
import spacy
import os
from glob import glob
import warnings
import sys
import logging
from spacy.tokens import Span
from taxonerd.extractor import TextExtractor


class TaxoNERD:
    def __init__(
        self,
        prefer_gpu=False,
        verbose=False,
        logger=None,
    ):
        self.logger = logger if logger else logging.getLogger(__name__)
        warnings.simplefilter("ignore")

        self.verbose = verbose
        self.extractor = TextExtractor(logger=self.logger)

        if prefer_gpu:
            import torch

            use_cuda = torch.cuda.is_available()
            self.logger.info("GPU is available" if use_cuda else "GPU not found")
            if use_cuda:
                spacy.require_gpu()
                self.logger.info("TaxoNERD will use GPU")

        self.nlp = None
        self.linker = None
        self.abbrev = None
        self.senten = None

    def load(
        self,
        model,
        exclude=[],
        linker=None,
        threshold=0.7,
    ):
        self.nlp = spacy.load(model, exclude=exclude)
        if "pysbd_sentencizer" not in exclude:
            from scispacy.custom_sentence_segmenter import pysbd_sentencizer

            if not Span.has_extension("sent_id"):
                Span.set_extension("sent_id", default=None)
            before = "parser" if "parser" not in exclude else "ner"
            self.nlp.add_pipe("pysbd_sentencizer", before=before)
            self.senten = "pysbd_sentencizer"
        if "taxo_abbrev_detector" not in exclude:
            from taxonerd.abbreviation import TaxonomicAbbreviationDetector

            self.nlp.add_pipe("taxo_abbrev_detector")
            self.abbrev = "taxo_abbrev_detector"
        if linker:
            from taxonerd.linking.linking_utils import KnowledgeBaseFactory
            from taxonerd.linking.candidate_generation import CandidateGenerator
            from taxonerd.linking.linking import EntityLinker

            self.nlp.add_pipe(
                "taxo_linker",
                config={
                    "linker_name": linker,
                    "resolve_abbreviations": "taxo_abbrev_detector" not in exclude,
                    "filter_for_definitions": False,
                    "k": 1,
                    "threshold": threshold,
                },
                name=f"{linker}_linker",
            )
            self.linker = linker if f"{linker}_linker" in self.nlp.pipe_names else None
        if self.verbose:
            self.logger.info(
                "Loaded model {}-{}".format(
                    self.nlp.meta["name"], self.nlp.meta["version"]
                )
            )
            self.logger.info(f"Pipeline components: {self.nlp.pipe_names}")
        return self.nlp

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
            raise FileNotFoundError("File {} not found".format(filename))
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
                and (ent.label_ in ["LIVB"])
                and (ent._.kb_ents if self.linker else True)
                # and ((ent not in doc._.abbreviations) if self.abbrev else True)
            )

        doc = self.nlp(text)
        ents = [ent for ent in doc.ents if is_valid_entity(ent, doc, text)]

        if ents and self.senten:
            sentences = {sent: id for id, sent in enumerate(doc.sents)}
            for ent in ents:
                ent._.sent_id = sentences[ent.sent]

        doc.set_ents(ents)
        # displacy.serve(doc, style="ent")
        return doc

    def doc_to_df(self, doc):
        def get_entity_dict(ent):
            ent_dict = {
                "offsets": "{} {} {}".format(ent.label_, ent.start_char, ent.end_char),
                "text": ent.text.replace("\n", " "),
            }
            if self.linker:
                ent_dict["entity"] = ent._.kb_ents
            if self.senten:
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
