import textract
import os
from glob import glob
import re


class TextExtractor:
    def __init__(self, logger=None):
        self.logger = logger

    def __call__(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError("No such file or directory: {}".format(path))
        if os.path.isdir(path):
            files = [f for f in glob(os.path.join(path, "*"))]
            for f in files:
                self.extract_from_file(f)
            return path
        elif os.path.isfile(path):
            output_path = self.extract_from_file(path)
            return output_path

    def extract_from_file(self, path):
        if os.path.basename(path).endswith(".txt"):
            return path
        output_path = self.get_output_path(path)
        self.logger.info("Extract text from {} to {}".format(path, output_path))
        try:
            text = textract.process(path).decode("utf-8")
        except Exception as e:
            self.logger.error("{}. In file {}. Skip.".format(e, path))
        else:
            with open(output_path, "w") as f:
                f.write(self.clean_text(text))
            return output_path
        return None

    # def extract_from_pdf_file(self, path):
    #     output_path = self.get_output_path(path)
    #     self.logger.info("Extract text from {} to {}".format(path, output_path))
    #     text = textract.process(path, method="pdfminer").decode("utf-8")
    #     text = self.post_processing(text)
    #     with open(output_path, "w") as f:
    #         f.write(text)
    #     return output_path

    def clean_text(self, text):
        # Remove non-ascii characters
        text = text.encode("ascii", "ignore").decode()
        # Replace \t by whitespace
        text = re.sub("\t+", " ", text)
        # Remove word break
        text = re.sub("-\n", "", text)
        # Remove newline characters in paragraphs
        text = re.sub("(?<!\n)\n(?!\n)", " ", text)
        # Remove multiple whitespaces
        text = re.sub(" +", " ", text)
        # Remove trailing newlines
        text = text.strip(" \n")
        # Remove punctuation at beginning
        text = re.sub("^([^\w\s\(\)]\s*)*", "", text)
        return text

    # def post_processing(self, text):
    #     # Replace \t by whitespace
    #     text = re.sub("\t+", " ", text)
    #     # Remove word break
    #     text = re.sub("-\n", "", text)
    #     # Remove newline characters in paragraphs
    #     text = re.sub("(?<!\n)\n(?!\n)", " ", text)
    #     # Remove multiple whitespaces
    #     text = re.sub(" +", " ", text)
    #     # Remove trailing newlines
    #     text = text.strip(" \n")
    #     return text

    def get_output_path(self, path):
        tokens = os.path.basename(path).split(".")
        if len(tokens):
            filename = ".".join(tokens[:-1]) + ".txt"
        dirname = os.path.dirname(path)
        output_path = os.path.join(dirname, filename)
        return output_path
