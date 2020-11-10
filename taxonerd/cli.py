import click
from .taxonerd import DeTaxer
import sys


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command()
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
@click.argument("text", required=False)
@click.pass_context
def eco(ctx, input_dir, output_dir, filename, with_abbrev, gpu, text):
    ner = DeTaxer(model="en_ner_ecology_md", with_abbrev=with_abbrev, with_gpu=gpu)

    if text:
        df = ner.find_entities(text, output_dir)
        df.to_csv(sys.stdout, sep="\t", header=False)
    elif input_dir:
        ner.find_all_files(input_dir, output_dir)
    elif filename:
        ner.find_in_file(filename, output_dir)


@cli.command()
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
@click.argument("text", required=False)
@click.pass_context
def bio(ctx, input_dir, output_dir, filename, with_abbrev, gpu, text):
    ner = DeTaxer(model="en_ner_biomedical_md", with_abbrev=with_abbrev, with_gpu=gpu)

    if text:
        df = ner.find_entities(text, output_dir)
        df.to_csv(sys.stdout, sep="\t", header=False)
    elif input_dir:
        ner.find_all_files(input_dir, output_dir)
    elif filename:
        ner.find_in_file(filename, output_dir)


def main():
    cli(obj={})


# @click.command()
# @click.option("--input-dir", "-i", type=str, help="Input directory")
# @click.option("--output-dir", "-o", type=str, help="Output directory")
# @click.option("--filename", "-f", type=str, help="Name of a text file")
# @click.option("--model", "-m", type=str, help="Path to NER model")
# @click.option(
#     "--with-abbrev",
#     "-a",
#     type=bool,
#     help="Add abbreviation detection to the pipeline",
#     is_flag=True,
# )
# # @click.option("--light", "-l", type=bool, help="Use light model", is_flag=True)
# @click.option("--gpu", type=bool, help="Use GPU if possible", is_flag=True)
# @click.argument("text", required=False)
# def eco(input_dir, output_dir, filename, model, text, with_abbrev, gpu):
#     """A deep neural model for taxonomic entity recognition"""
#
#     ner = DeTaxer(model_path=model, with_abbrev=with_abbrev, with_gpu=gpu)
#
#     if text:
#         df = ner.find_entities(text, output_dir)
#         df.to_csv(sys.stdout, sep="\t", header=False)
#     elif input_dir:
#         ner.find_all_files(input_dir, output_dir)
#     elif filename:
#         ner.find_in_file(filename, output_dir)


# if __name__ == "__main__":
#     eco()
