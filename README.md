<img src="https://github.com/nleguillarme/taxonerd/blob/main/taxonerd_logo.png" width="40%">

Looking for taxon mentions in text? Ask TaxoNERD

* [Features](#features)
* [Installation](#installation)
* [Usage](#usage)

## Features

TaxoNERD is a domain-specific tool for recognizing taxon mentions in the biodiversity literature.

* Based on the en_core_sci_md model from [scispaCy](https://allenai.github.io/scispacy/), fine-tuned on an ecological corpus
* Find scientific names, english common names and user-defined abbreviations
* Can link taxon mentions to entities in a reference taxonomy (GBIF Backbone and TAXREF at the moment, more to come)
* TaxoNERD is fast (once the model is loaded), and can run on CPU or GPU
* Entity linking does not need an internet connection, but may require a lot of RAM depending on the size of the taxonomy (e.g. GBIF Backbone -> ~12.5Gb)
* Thanks to [textract](https://textract.readthedocs.io/en/stable/), TaxoNERD can extract taxon mentions from (almost) any document (including txt, pdf, csv, xls, jpg, png, and many other formats)
* Available as a command-line tool and a python module

## Installation

TaxoNERD is only available for Python 3.6+

    $ pip install taxonerd
    $ pip install https://github.com/nleguillarme/taxonerd/releases/download/v0.1.1/en_ner_eco_md-0.1.1.tar.gz

Entity linker files are downloaded and cached the first time the linker is used. This may take some time, but it should only be done once.
Currently (v1.0.0), there are 2 supported linkers:

* gbif_backbone: Links to [GBIF Backbone Taxonomy (2019-09-06)](https://www.gbif.org/fr/dataset/d7dddbf4-2cf0-4f39-9b2a-bb099caae36c) (~9.5M names for ~3.5M taxa).
* taxref: Links to [TAXREF (v13)](https://inpn.mnhn.fr/telechargement/referentielEspece/taxref/13.0/menu) (~1.2M names for ~267k taxa).

## Usage

### Use as command-line tool

```
Usage: taxonerd ask [OPTIONS] [INPUT_TEXT]

Options:
  -m, --model TEXT       A spaCy taxonomic NER model
  -i, --input-dir TEXT   Input directory
  -o, --output-dir TEXT  Output directory
  -f, --filename TEXT    Input text file
  -a, --with-abbrev      Add abbreviation detector to the pipeline
  -l, --link-to TEXT     Add entity linker to the pipeline
  -t, --thresh FLOAT     Similarity threshold for entity candidates (default = 0.7)
  --gpu                  Use GPU if available
  -v, --verbose          Verbose mode
  --help                 Show this message and exit.
  ```

  #### Examples

  ##### Taxonomic NER from the terminal

``` console
$ taxonerd ask "Brown bears (Ursus arctos), which are widely distributed throughout the northern hemisphere, are recognised as opportunistic omnivores"
T0	LIVB 0 11	Brown bears
T1	LIVB 13 25	Ursus arctos
```

  ##### Taxonomic NER with entity linking from the terminal

``` console
$ taxonerd ask -l gbif_backbone "Brown bears (Ursus arctos), which are widely distributed throughout the northern hemisphere, are recognised as opportunistic omnivores"
T0	LIVB 0 11	Brown bears	[('GBIF:2433433', 'Brown Bear', 0.8313919901847839)]
T1	LIVB 13 25	Ursus arctos	[('GBIF:2433433', 'Ursus arctos', 1.0)]

$ taxonerd ask -l gbif_backbone -t 0.85 "Brown bears (Ursus arctos), which are widely distributed throughout the northern hemisphere, are recognised as opportunistic omnivores"
T0	LIVB 13 25	Ursus arctos	[('GBIF:2433433', 'Ursus arctos', 1.0)]
```

  ##### Taxonomic NER from a text file (with abbreviation detection)

``` console
$ taxonerd ask --with-abbrev -f test_txt/sample_text1.txt
T0	LIVB 4 21	pinewood nematode
T1	LIVB 23 26	PWN
T2	LIVB 29 55	Bursaphelenchus xylophilus
T3	LIVB 180 188	Serratia
T4	LIVB 326 348	Serratia grimesii BXF1
T5	LIVB 424 428	BXF1
T7	LIVB 371 374	PWN
T8	LIVB 241 244	PWN
```

  ##### Taxonomic NER from a directory containing text files, with results written in the output directory

``` console
$ taxonerd ask -i test_txt -o test_ann
$ ls test_ann/
sample_text1.ann  sample_text2.ann
$ cat test_ann/sample_text2.ann
T0	LIVB 700 711	Brown bears
T1	LIVB 713 725	Ursus arctos
T2	LIVB 1906 1912	salmon
T3	LIVB 1974 1980	salmon
T4	LIVB 2123 2129	salmon
T5	LIVB 2392 2401	Sika deer
T6	LIVB 2403 2416	Cervus nippon
T7	LIVB 3135 3141	salmon
T8	LIVB 3146 3150	deer
T9	LIVB 3188 3199	chum salmon
T10	LIVB 3201 3218	Oncorhynchus keta
T11	LIVB 3280 3289	Sika deer
T12	LIVB 3363 3375	O. gorbuscha
T13	LIVB 3381 3392	chum salmon
```

### Use as python module

``` python
>>> from taxonerd import TaxoNERD
>>> ner = TaxoNERD(model="en_ner_eco_md", with_gpu=False, with_abbrev=False) # Add with_linking="gbif_backbone" or with_linking="taxref" to activate entity linking
```
#### Examples

  ##### Find taxonomic entities in an input string

``` python
>>> ner.find_entities("Brown bears (Ursus arctos), which are widely distributed throughout the northern hemisphere, are recognised as opportunistic omnivore")
       offsets          text
T0   LIVB 0 11   Brown bears
T1  LIVB 13 25  Ursus arctos
```

  ##### Find taxonomic entities in an input file

``` python
>>> ner.find_in_file("./test_txt/sample_text1.txt", output_dir=None)
T0	LIVB 4 21	pinewood nematode
T1	LIVB 23 26	PWN
T2	LIVB 29 55	Bursaphelenchus xylophilus
T3	LIVB 180 188	Serratia
T4	LIVB 326 348	Serratia grimesii BXF1
T5	LIVB 424 428	BXF1
```

  ##### Find taxonomic entities in all the files in the input directory, and write the results in the output directory

``` python
>>> ner.find_all_files("./test_txt", "./test_ann")
```

## License

License: MIT

## Authors

TaxoNERD was written by [nleguillarme](https://github.com/nleguillarme/).
