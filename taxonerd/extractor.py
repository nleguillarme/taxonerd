import textract
import os
from glob import glob


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
        text = textract.process(path).decode("utf-8")
        self.logger.info("Extract text from {} to {}".format(path, output_path))
        with open(output_path, "w") as f:
            f.write(text)
        return output_path

    def get_output_path(self, path):
        tokens = os.path.basename(path).split(".")
        if len(tokens):
            filename = ".".join(tokens[:-1]) + ".txt"
        dirname = os.path.dirname(path)
        output_path = os.path.join(dirname, filename)
        return output_path
