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
# @click.option(
#     "--model",
#     "-m",
#     type=str,
#     help="A spaCy taxonomic NER model",
#     # default="en_ner_eco_md",
# )
@click.option(
    "--focus-on", type=str, help="Focus on either speed or accuracy", default="speed"
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
    help="Similarity threshold for entity candidates (default = 0.7)",
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
    focus_on,
    input_text,
):

    logger = logging.getLogger(__name__)
    if verbose:
        logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

    ner_model = (
        "en_ner_eco_biobert"
        if (focus_on and focus_on == "accuracy")
        else "en_ner_eco_md"
    )

    prefer_gpu = prefer_gpu if prefer_gpu else False  # (focus_on == "accuracy")

    ner = TaxoNERD(
        model=ner_model,
        with_abbrev=with_abbrev,
        with_sentence=with_sentence,
        with_linking=link_to,
        threshold=thresh,
        prefer_gpu=prefer_gpu,
        verbose=verbose,
        logger=logger,
    )

    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    if input_text:
        df = ner.find_in_text(input_text)
        df.to_csv(sys.stdout, sep="\t", header=False)
    else:
        dfs = {}
        if filename:
            dfs[os.path.basename(filename)] = ner.find_in_file(filename, output_dir)
        elif input_dir:
            dfs = ner.find_in_corpus(input_dir, output_dir)

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
