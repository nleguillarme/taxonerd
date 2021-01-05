import pandas as pd
import spacy
import os
from glob import glob
import warnings
import sys
import logging

from scispacy.abbreviation import AbbreviationDetector


class TaxoNERD:
    def __init__(
        self,
        model="en_ner_eco_md",
        with_abbrev=False,
        with_linking=None,
        threshold=0.7,
        with_gpu=False,
        verbose=False,
        logger=None,
    ):
        self.logger = logger if logger else logging.getLogger(__name__)
        warnings.simplefilter("ignore")
        self.verbose = verbose
        if with_gpu:
            self.logger.info("Use GPU")
            spacy.prefer_gpu()
        self.logger.info("Load model {}".format(model))
        self.nlp = spacy.load(model)
        self.logger.info(
            "Loaded model {}-{}".format(self.nlp.meta["name"], self.nlp.meta["version"])
        )

        self.with_abbrev = with_abbrev
        if self.with_abbrev:
            if self.verbose:
                logger.info(f"Add AbbreviationDetector to pipeline")
            abbreviation_pipe = AbbreviationDetector(self.nlp)
            self.nlp.add_pipe(abbreviation_pipe)

        self.with_linking = with_linking != None
        if self.with_linking:
            kb_name = with_linking if with_linking != "" else "gbif_backbone"
            if self.verbose:
                logger.info(f"Add EntityLinker {kb_name} to pipeline")
            linker = self.create_linker(kb_name, threshold)
            self.nlp.add_pipe(linker)

    def create_linker(self, kb_name, threshold):
        from taxonerd.linking.linking_utils import KnowledgeBaseFactory
        from taxonerd.linking.candidate_generation import CandidateGenerator
        from taxonerd.linking.linking import EntityLinker

        kb = KnowledgeBaseFactory().get_kb(kb_name)

        return EntityLinker(
            candidate_generator=CandidateGenerator(
                name=kb_name, kb=kb, verbose=self.verbose
            ),
            resolve_abbreviations=self.with_abbrev,
            filter_for_definitions=False,
            k=1,
            threshold=threshold,
        )

    def find_all_files(self, input_dir, output_dir=None):
        for filename in glob(os.path.join(input_dir, "*.txt")):
            self.find_in_file(filename, output_dir)

    def find_in_file(self, filename, output_dir=None):
        if not os.path.exists(filename):
            raise FileNotFoundError("file {} not found".format(path))
        self.logger.info("Extract taxa from file {}".format(filename))
        with open(filename, "r") as f:
            text = f.read()
        ann_filename = ".".join(os.path.basename(filename).split(".")[:-1]) + ".ann"
        df = self.find_entities(text)
        if output_dir:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            df.to_csv(os.path.join(output_dir, ann_filename), sep="\t", header=False)
        else:
            df.to_csv(sys.stdout, sep="\t", header=False)

    def get_entity_dict(self, ent, text):
        ent_dict = {
            "offsets": "LIVB {} {}".format(ent.start_char, ent.end_char),
            "text": text[ent.start_char : ent.end_char].replace("\n", " "),
        }
        if self.with_linking:
            ent_dict["entity"] = ent._.kb_ents
        return ent_dict

    def find_entities(self, text):
        doc = self.nlp(text)
        entities = []
        if len(doc.ents) > 0:
            entities = [
                self.get_entity_dict(ent, text)
                for ent in doc.ents
                if (
                    "\n" not in text[ent.start_char : ent.end_char].strip("\n")
                    and ent.label_ == "LIVB"
                )
            ]
            for ent in doc.ents:
                if ent.label_ != "LIVB":
                    raise ValueError(ent.label_)
        if self.with_abbrev:
            entities += (
                self.get_abbreviated_tax_entity(text, entities, doc._.abbreviations)
                if len(doc._.abbreviations) > 0
                else []
            )

        df = pd.DataFrame(entities)
        df = df.dropna()
        df = df.loc[df.astype(str).drop_duplicates().index]
        df = df.reset_index(drop=True)
        return df.rename("T{}".format)

    def get_abbreviated_tax_entity(self, text, entities, abbreviations):
        ents = [ent["text"] for ent in entities]
        abbreviations = [
            self.get_entity_dict(abrv, text)
            # {
            #     "offsets": "LIVB {} {}".format(abrv.start_char, abrv.end_char),
            #     "text": text[abrv.start_char : abrv.end_char]
            #     + ";"
            #     + abrv._.long_form.text,
            #     "entity": abrv._.kb_ents,
            # }
            for abrv in abbreviations
            if abrv._.long_form.text in ents
        ]
        return abbreviations
