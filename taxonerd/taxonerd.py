import pandas as pd
import spacy
import os
from glob import glob
import warnings
import sys

from scispacy.abbreviation import AbbreviationDetector


class DeTaxer:
    def __init__(self, model="en_ner_ecology_md", with_abbrev=False, with_gpu=False):
        warnings.simplefilter("ignore")
        if with_gpu:
            print("Use GPU")
            spacy.prefer_gpu()
        # if model_path:
        #     self.nlp = spacy.load(model_path)
        print("Load model {}".format(model))
        self.nlp = spacy.load(model)

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
                if "\n" not in text[ent.start_char : ent.end_char].strip("\n")
            ]
        if self.with_abbrev:
            entities += (
                self.get_abbreviated_tax_entity(entities, doc._.abbreviations)
                if len(doc._.abbreviations) > 0
                else []
            )

        df = pd.DataFrame(entities)
        df = df.rename("T{}".format)
        return df

    def get_abbreviated_tax_entity(self, entities, abbreviations):
        ents = [ent["text"] for ent in entities]
        abbreviations = [
            {
                "offsets": "LIVB {} {}".format(abrv.start_char, abrv.end_char),
                "text": abrv._.long_form,
            }
            for abrv in abbreviations
            if abrv._.long_form.text in ents
        ]
        return abbreviations

    # def reconstruct_entities(self, tokens):
    #     start = None
    #     for i in range(len(tokens)):
    #         if tokens[i].ent_type_ == "B-LIVB":
    #             start = tokens[i].idx
    #             end = tokens[i].idx + len(tokens[i])
    #             for j in range(i + 1, len(tokens)):
    #                 if tokens[j].ent_type_ == "I-LIVB":
    #                     end = tokens[j].idx + len(tokens[j])
    #                 else:
    #                     yield start, end
    #                     i = j
    #                     start = None
    #                     break
    #     if start:
    #         yield start, end
