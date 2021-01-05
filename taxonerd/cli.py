import click
from taxonerd import TaxoNERD
from taxonerd.extractor import TextExtractor
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
@click.option("--filename", "-f", type=str, help="Input text file")
@click.option(
    "--with-abbrev",
    "-a",
    type=bool,
    help="Add abbreviation detector to the pipeline",
    is_flag=True,
)
@click.option("--link-to", "-l", type=str, help="Add entity linker to the pipeline")
@click.option(
    "--thresh",
    "-t",
    help="Similarity threshold for entity candidates (default = 0.7)",
    default=0.7,
)
@click.option("--gpu", type=bool, help="Use GPU if available", is_flag=True)
@click.option("--verbose", "-v", type=bool, help="Verbose mode", is_flag=True)
@click.argument("input_text", required=False)
def ask(
    model,
    input_dir,
    output_dir,
    filename,
    with_abbrev,
    link_to,
    thresh,
    gpu,
    verbose,
    input_text,
):

    logger = logging.getLogger(__name__)
    if verbose:
        logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

    ext = TextExtractor(logger=logger)
    ner = TaxoNERD(
        model=model,
        with_abbrev=with_abbrev,
        with_linking=link_to,
        threshold=thresh,
        with_gpu=gpu,
        verbose=verbose,
        logger=logger,
    )

    if input_text:
        df = ner.find_entities(input_text)
        df.to_csv(sys.stdout, sep="\t", header=False)
    elif input_dir:
        input_dir = ext(input_dir)
        ner.find_all_files(input_dir, output_dir)
    elif filename:
        filename = ext(filename)
        ner.find_in_file(filename, output_dir)


def main():
    cli()
