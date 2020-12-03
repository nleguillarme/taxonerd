<img src="https://github.com/nleguillarme/taxonerd/blob/main/taxonerd_logo.png" width="40%">

Looking for taxon mentions in text? Ask TaxoNERD

* [Features](#features)
* [Installation](#installation)
* [Usage](#usage)

## Features

* Based on the en_core_sci_md model from [scispaCy](https://allenai.github.io/scispacy/), fine-tuned on ecological and biomedical datasets
* Find scientific names, common names and user-defined abbreviations
* Lightning-fast on CPU, can use GPU to speed-up the recognition process
* Available as a command-line tool and a python library

## Installation

    $ pip install .
    $ pip install https://github.com/nleguillarme/taxonerd/releases/download/v0.1.1/en_ner_eco_md-0.1.1.tar.gz


## Usage

To use it:

    $ taxonerd --help
