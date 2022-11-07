import click
import sys
import os
import logging
import logging.config
from taxonerd import TaxoNERD


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--model",
    "-m",
    type=str,
    help="A TaxoNERD model [default = en_ner_eco_md]",
    default="en_core_eco_md",
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
@click.option(
    "--with-sentence",
    "-s",
    type=bool,
    help="Add sentence segmenter to the pipeline",
    is_flag=True,
)
@click.option("--link-to", "-l", type=str, help="Add entity linker to the pipeline")
@click.option(
    "--thresh",
    "-t",
    help="Similarity threshold for entity linking [default = 0.7]",
    default=0.7,
)
@click.option("--prefer-gpu", type=bool, help="Use GPU if available", is_flag=True)
@click.option("--verbose", "-v", type=bool, help="Verbose mode", is_flag=True)
@click.argument("input_text", required=False)
def ask(
    input_dir,
    output_dir,
    filename,
    with_abbrev,
    with_sentence,
    link_to,
    thresh,
    prefer_gpu,
    verbose,
    model,
    input_text,
):

    logger = logging.getLogger(__name__)
    if verbose:
        logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

    ner_model = model

    prefer_gpu = prefer_gpu if prefer_gpu else False  # (focus_on == "accuracy")

    nerd = TaxoNERD(
        prefer_gpu=prefer_gpu,
        verbose=verbose,
        logger=logger,
    )

    exclude = ["tagger", "attribute_ruler", "lemmatizer", "parser"]
    if not with_abbrev:
        exclude.append("taxo_abbrev_detector")
    if not with_sentence:
        exclude.append("pysbd_sentencizer")
    nerd.load(ner_model, exclude=exclude, linker=link_to, threshold=thresh)

    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    if input_text:
        df = nerd.find_in_text(input_text)
        df.to_csv(sys.stdout, sep="\t", header=False)
    else:
        dfs = {}
        if filename:
            dfs[os.path.basename(filename)] = nerd.find_in_file(filename, output_dir)
        elif input_dir:
            dfs = nerd.find_in_corpus(input_dir, output_dir)

        if not output_dir:
            if len(dfs) > 1:
                for filename in dfs:
                    dfs[filename] = dfs[filename].set_index(
                        filename + "_" + dfs[filename].index.astype(str)
                    )
            for filename in dfs:
                dfs[filename].to_csv(sys.stdout, sep="\t", header=False)


def main():
    cli()
