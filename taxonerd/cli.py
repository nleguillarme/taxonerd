import click
from .taxonerd import TaxoNERD
import sys
import logging
import logging.config


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--model",
    "-m",
    type=str,
    help="A spaCy taxonomic NER model",
    default="en_ner_eco_md",
)
@click.option("--input-dir", "-i", type=str, help="Input directory")
@click.option("--output-dir", "-o", type=str, help="Output directory")
@click.option("--filename", "-f", type=str, help="Name of a text file")
@click.option(
    "--with-abbrev",
    "-a",
    type=bool,
    help="Add abbreviation detection to the pipeline",
    is_flag=True,
)
@click.option("--gpu", type=bool, help="Use GPU if possible", is_flag=True)
@click.option("-v", type=bool, help="Verbose mode", is_flag=True)
@click.argument("text", required=False)
def ask(model, input_dir, output_dir, filename, with_abbrev, gpu, v, text):

    logger = logging.getLogger(__name__)
    if v:
        logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

    ner = TaxoNERD(model=model, with_abbrev=with_abbrev, with_gpu=gpu, logger=logger)

    if text:
        df = ner.find_entities(text)
        df.to_csv(sys.stdout, sep="\t", header=False)
    elif input_dir:
        ner.find_all_files(input_dir, output_dir)
    elif filename:
        ner.find_in_file(filename, output_dir)


def main():
    cli()
