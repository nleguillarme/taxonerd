import pandas as pd
import spacy
import os
from glob import glob
import warnings
import sys

from scispacy.abbreviation import AbbreviationDetector


class TaxoNERD:
    def __init__(
        self, model="en_ner_eco_md", with_abbrev=False, with_gpu=False, logger=None
    ):
        self.logger = logger
        warnings.simplefilter("ignore")
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
            abbreviation_pipe = AbbreviationDetector(self.nlp)
            self.nlp.add_pipe(abbreviation_pipe)

    def find_all_files(self, input_dir, output_dir):
        for filename in glob(os.path.join(input_dir, "*.txt")):
            self.find_in_file(filename, output_dir)

    def find_in_file(self, filename, output_dir):
        with open(filename, "r") as f:
            text = f.read()
        ann_filename = ".".join(os.path.basename(filename).split(".")[:-1]) + ".ann"
        df = self.find_entities(text)
        if output_dir:
            df.to_csv(os.path.join(output_dir, ann_filename), sep="\t", header=False)
        else:
            df.to_csv(sys.stdout, sep="\t", header=False)

    def find_entities(self, text):
        doc = self.nlp(text)
        entities = []
        if len(doc.ents) > 0:
            entities = [
                {
                    "offsets": "LIVB {} {}".format(ent.start_char, ent.end_char),
                    "text": text[ent.start_char : ent.end_char].replace("\n", " "),
                }
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
        df = df.rename("T{}".format)
        return df

    def get_abbreviated_tax_entity(self, text, entities, abbreviations):
        ents = [ent["text"] for ent in entities]
        abbreviations = [
            {
                "offsets": "LIVB {} {}".format(abrv.start_char, abrv.end_char),
                "text": text[abrv.start_char : abrv.end_char]
                + ";"
                + abrv._.long_form.text,
            }
            for abrv in abbreviations
            if abrv._.long_form.text in ents
        ]
        return abbreviations
