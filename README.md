![](https://i.ibb.co/G09fX98/taxonerd-logo.png)

Looking for taxon mentions in text? Ask TaxoNERD

* [Features](#features)
* [Models](#models)
* [Installation](#installation)
* [Usage](#usage)
* [Extensions](#extensions)

I would be happy to hear about your use of TaxoNERD : what is your use case? How did TaxoNERD help you? What could make TaxoNERD even more helpful? Please feel free to drop me an email (nicolas[dot]leguillarme[at]univ-grenoble-alpes[dot]fr) or to open an issue.

## Cite TaxoNERD

Le Guillarme, N., & Thuiller, W. (2022). [TaxoNERD: deep neural models for the recognition of taxonomic entities in the ecological and evolutionary literature](https://doi.org/10.1111/2041-210X.13778). Methods in Ecology and Evolution, 13(3), 625-641.

## Features

TaxoNERD is a domain-specific tool for recognizing taxon mentions in the biodiversity literature.

:tada: **New models are out ! Now including additional NLP components (tagger, attribut ruler, lemmatizer, parser) and more accurate common names detection.**

* TaxoNERD is available as a command-line tool, a Python module, a spaCy pipeline, **and a R package thanks to reticulate**.
* TaxoNERD provides two architectures : the **md** architecture uses spaCy's standard Tok2Vec layer with word vectors for speed, while the **biobert** architecture uses a Transformer-based pretrained language model (dmis-lab/biobert-v1.1) for accuracy.
* TaxoNERD finds scientific names, common names, abbreviated species names and user-defined abbreviations.
* TaxoNERD can link taxon mentions to entities in a reference taxonomy (NCBI Taxonomy, GBIF Backbone and TAXREF at the moment, more to come).
* TaxoNERD is fast (once the model is loaded), and can run on CPU or GPU.
* Entity linking does not need an internet connection, but may require a lot of RAM depending on the size of the taxonomy (e.g. GBIF Backbone -> ~12.5Gb).
* Thanks to [textract](https://textract.readthedocs.io/en/stable/), **TaxoNERD can extract taxon mentions from (almost) any document** (including txt, pdf, csv, xls, jpg, png, and many other formats). With TaxoNERD, the detection of taxonomic entities in a JPG file is as simple as that:

<img width="50%" align="left" src="https://github.com/nleguillarme/taxonerd/raw/main/tests/test_data/test_jpg/test.jpg">


``` console
taxonerd ask -m en_core_eco_weak_biobert -f ./tests/test_data/test_jpg/test.jpg 
T0	LIVB 180 192	Harbour seal
T1	LIVB 194 208	Phoca vitulina
T2	LIVB 361 375	Pacific salmon
T3	LIVB 377 394	Oncorhynchus spp.
T4	LIVB 455 467	harbour seal
T5	LIVB 714 718	seal
T6	LIVB 793 805	harbour seal
T7	LIVB 1127 1133	fishes
T8	LIVB 1137 1148	cephalopods
```


## Models

| Model               |      Description      |  Install URL |
|---------------------|:-------------:|------:|
| en_core_eco_md      | A full spaCy pipeline for ecological data with 50k word vectors (taken from [en_core_sci_md](https://allenai.github.io/scispacy/)) fine-tuned on a gold standard corpus. | [Download](https://github.com/nleguillarme/taxonerd/releases/download/v1.5.0/en_core_eco_md-1.0.2.tar.gz)      |
| en_core_eco_biobert | A full spaCy pipeline for ecological data with dmis-lab/biobert-v1.1 as the transformer model, fine-tuned on a gold standard corpus.                               | [Download](https://github.com/nleguillarme/taxonerd/releases/download/v1.5.0/en_core_eco_biobert-1.0.2.tar.gz) |
| en_core_eco_weak_md | A full spaCy pipeline for ecological data with 50k word vectors (taken from [en_core_sci_md](https://allenai.github.io/scispacy/)) fine-tuned on a silver standard corpus. | [Download](https://github.com/nleguillarme/taxonerd/releases/download/v1.5.0/en_core_eco_weak_md-1.0.0.tar.gz)    |
| en_core_eco_weak_biobert | A full spaCy pipeline for ecological data with dmis-lab/biobert-v1.1 as the transformer model, fine-tuned on a silver standard corpus.                               | [Download](https://github.com/nleguillarme/taxonerd/releases/download/v1.5.0/en_core_eco_weak_biobert-1.0.0.tar.gz) |

### What model should I choose ?

If you have access to a GPU, we recommend using one of the biobert models as they tend to be more accurate than the md models.

The en_core_eco_weak_md and en_core_eco_weak_biobert have been fine-tuned on a silver standard corpus generated using weak supervision. Therefore, they have been trained on a much larger amount of (noisy) data than their gold standard counterparts. As a result, they tend to have better recall, especially with respect to common names detection. They also have high precision. Nevertheless, their performance has not been accurately evaluated.

If you do not trust weakly-supervised data and you are not really interested in detecting common names, en_core_eco_md and en_core_eco_biobert are for you. These models have been fine-tuned on a gold standard corpus (a combination of [COPIOUS](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6351503/) and [Bacteria Biotope 2019](https://aclanthology.org/D19-5719/)) and their performance has been benchmarked in our paper.

## Installation

### TaxoNERD for Python

Installing the package from pip will automatically install all dependencies, including pandas, spaCy, scispaCy and textract. Make sure you install this package before you install the models. Also note that this package requires Python 3.8+ and spaCy v3.4+.

    $ pip install taxonerd

For GPU support, find your CUDA version using `nvcc --version` and add the version in brackets, e.g. `pip install taxonerd[cuda113]` for CUDA 11.3. See [setup.cfg](setup.cfg) for supported CUDA versions.

To download the models:

    $ pip install https://github.com/nleguillarme/taxonerd/releases/download/v1.5.0/en_core_eco_md-1.0.2.tar.gz
    $ pip install https://github.com/nleguillarme/taxonerd/releases/download/v1.5.0/en_core_eco_biobert-1.0.2.tar.gz
    $ pip install https://github.com/nleguillarme/taxonerd/releases/download/v1.5.0/en_core_eco_weak_md-1.0.0.tar.gz
    $ pip install https://github.com/nleguillarme/taxonerd/releases/download/v1.5.0/en_core_eco_weak_biobert-1.0.0.tar.gz

Entity linker files are downloaded and cached the first time the linker is used. This may take some time, but it should only be done once. Currently (v1.5.0), there are 3 supported linkers:

* gbif_backbone: Links to [GBIF Backbone Taxonomy (2019-09-06)](https://www.gbif.org/fr/dataset/d7dddbf4-2cf0-4f39-9b2a-bb099caae36c) (~9.5M names for ~3.5M taxa).
* taxref: Links to [TAXREF (v13)](https://inpn.mnhn.fr/telechargement/referentielEspece/taxref/13.0/menu) (~1.2M names for ~267k taxa).
* ncbi_taxonomy: Links to [The NCBI Taxonomy](https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/) (~3.4M names).
<!-- * ncbi_taxonomy_lite: Links to [The NCBI Taxonomy](https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/) from which we removed virus names and added abreviated species name (e.g. *P. marina*) (~3.5M names). The ncbi_taxonomy_lite linker supports abbreviated species names out-of-the-box. This means that even if you do not use the abbreviation detector, abbreviated species names such as *P. marina* can be linked to the corresponding taxonomic unit *Pirellula marina* (NCBI:214). -->

### TaxoNERD for R

    > install.packages("https://github.com/nleguillarme/taxonerd/releases/download/v1.5.0/taxonerd_for_R_1.5.0.tar.gz", repos=NULL)
    > vignette("taxonerd") # See vignette for more information on how to install and use TaxoNERD for R

## Usage

TaxoNERD can be used as:
* [a command-line tool](#use-as-command-line-tool)
* [a Python module](#use-as-python-module)
* [a spaCy pipeline](#use-as-spacy-pipeline)

### Use as command-line tool

``` console
$ taxonerd ask --help
Usage: taxonerd ask [OPTIONS] [INPUT_TEXT]

Options:
  -m, --model TEXT       A TaxoNERD model [default = en_ner_eco_md]
  -i, --input-dir TEXT   Input directory
  -o, --output-dir TEXT  Output directory
  -f, --filename TEXT    Input text file
  -a, --with-abbrev      Add abbreviation detector to the pipeline
  -s, --with-sentence    Add sentence segmenter to the pipeline
  -l, --link-to TEXT     Add entity linker to the pipeline
  -t, --thresh FLOAT     Similarity threshold for entity linking [default =
                         0.7]

  --prefer-gpu           Use GPU if available
  -v, --verbose          Verbose mode
  --help                 Show this message and exit.
```

  #### Examples

  ##### Taxonomic NER from the terminal

``` console
$ taxonerd ask -m en_core_eco_biobert "Brown bears (Ursus arctos), which are widely distributed throughout the northern hemisphere, are recognised as opportunistic omnivores"
T0	LIVB 0 11	Brown bears
T1	LIVB 13 25	Ursus arctos
```

  ##### Taxonomic NER with entity linking from the terminal

``` console
$ taxonerd ask -m en_core_eco_biobert -l gbif_backbone "Brown bears (Ursus arctos), which are widely distributed throughout the northern hemisphere, are recognised as opportunistic omnivores"
T0	LIVB 0 11	Brown bears	[('GBIF:2433433', 'Brown Bear', 0.8313919901847839)]
T1	LIVB 13 25	Ursus arctos	[('GBIF:2433433', 'Ursus arctos', 1.0)]

$ taxonerd ask -m en_core_eco_biobert -l gbif_backbone -t 0.85 "Brown bears (Ursus arctos), which are widely distributed throughout the northern hemisphere, are recognised as opportunistic omnivores"
T0	LIVB 13 25	Ursus arctos	[('GBIF:2433433', 'Ursus arctos', 1.0)]
```

  ##### Taxonomic NER from a text file (with abbreviation detection)

``` console
$ taxonerd ask -m en_core_eco_biobert --with-abbrev -f ./tests/test_data/test_txt/test1.txt
T0	LIVB 4 21	pinewood nematode
T1	LIVB 23 26	PWN
T2	LIVB 29 55	Bursaphelenchus xylophilus
T3	LIVB 57 70	B. xylophilus
T4	LIVB 99 108	pine wilt
T5	LIVB 196 204	Serratia
T6	LIVB 257 260	PWN
T7	LIVB 342 364	Serratia grimesii BXF1
T8	LIVB 387 390	PWN
T9	LIVB 440 444	BXF1
```

  ##### Taxonomic NER from a directory containing text files, with results written in the output directory

``` console
$ taxonerd ask --focus-on accuracy -i ./tests/test_data/test_txt -o test_ann
$ ls test_ann/
test1.ann  test2.ann
$ cat test_ann/test2.ann
T0	LIVB 700 711	Brown bears
T1	LIVB 713 725	Ursus arctos
T2	LIVB 1062 1073	brown bears
T3	LIVB 1161 1172	brown bears
T4	LIVB 1339 1350	brown bears
T5	LIVB 1555 1565	brown bear
T6	LIVB 1782 1793	brown bears
T7	LIVB 1863 1874	brown bears
T8	LIVB 1958 1969	brown bears
T9	LIVB 1974 1980	salmon
T10	LIVB 2026 2037	brown bears
T11	LIVB 2219 2230	brown bears
T12	LIVB 2392 2401	Sika deer
T13	LIVB 2403 2416	Cervus nippon
T14	LIVB 2555 2559	deer
T15	LIVB 2594 2604	brown bear
T16	LIVB 2798 2808	brown bear
T17	LIVB 3146 3150	deer
T18	LIVB 3188 3199	chum salmon
T19	LIVB 3201 3218	Oncorhynchus keta
T20	LIVB 3280 3289	Sika deer
T21	LIVB 3350 3361	pink salmon
T22	LIVB 3363 3375	O. gorbuscha
T23	LIVB 3381 3392	chum salmon
T24	LIVB 3518 3528	Brown bear
T25	LIVB 4001 4012	brown bears
T26	LIVB 4071 4082	brown bears
```

### Use as python module

``` python
>>> from taxonerd import TaxoNERD
>>> taxonerd = TaxoNERD(prefer_gpu=False)
>>> nlp = taxonerd.load(model="en_core_eco_md", exclude=[], linker="taxref", threshold=0.7)
>>> nlp.pipe_names
['tok2vec', 'tagger', 'attribute_ruler', 'lemmatizer', 'pysbd_sentencizer', 'parser', 'ner', 'taxo_abbrev_detector', 'taxref_linker']
```

**N.B.** By default, all components are included in the pipeline. Use the ``exclude`` argument to specify the components to exclude. Excluded components won’t be loaded. This may speed up the detection process. The minimal pipeline for taxonomic NER is ``['tok2vec', 'ner']``.

#### Examples

  ##### Find taxonomic entities in an input string

``` python
>>> taxonerd.find_in_text("Brown bears (Ursus arctos), which are widely distributed throughout the northern hemisphere, are recognised as opportunistic omnivore")
      offsets           text                               entity  sent
T0  LIVB 13 25  Ursus arctos  [(TAXREF:60826, Ursus arctos, 1.0)]     0
```

  ##### Find taxonomic entities in an input file

``` python
>>> taxonerd.find_in_file("./tests/test_data/test_txt/test2.txt", output_dir=None)
            offsets               text                                             entity  sent
T0     LIVB 713 725       Ursus arctos                [(TAXREF:60826, Ursus arctos, 1.0)]     4
T1   LIVB 1974 1980             salmon      [(TAXREF:730671, Salmonia, 0.85158771276474)]    12
T2   LIVB 2392 2401          Sika deer                   [(TAXREF:61025, Sika Deer, 1.0)]    14
T3   LIVB 2403 2416      Cervus nippon               [(TAXREF:61025, Cervus nippon, 1.0)]    14
T4   LIVB 3135 3141             salmon      [(TAXREF:730671, Salmonia, 0.85158771276474)]    18
T5   LIVB 3146 3150               deer                       [(TAXREF:186210, deer, 1.0)]    18
T6   LIVB 3188 3199        chum salmon    [(TAXREF:730671, Salmonia, 0.7018352746963501)]    19
T7   LIVB 3201 3218  Oncorhynchus keta  [(TAXREF:195439, Oncorhynchus, 0.8319146037101...    19
T8   LIVB 3280 3289          Sika deer                   [(TAXREF:61025, Sika Deer, 1.0)]    19
T9   LIVB 3350 3361        pink salmon                 [(TAXREF:67798, Pink Salmon, 1.0)]    20
T10  LIVB 3381 3392        chum salmon    [(TAXREF:730671, Salmonia, 0.7018352746963501)]    20
T11  LIVB 3481 3485               deer                       [(TAXREF:186210, deer, 1.0)]    20
```

  ##### Find taxonomic entities in all the files in the input directory, and write the results in the output directory

``` python
>>> taxonerd.find_in_corpus("./tests/test_data/test_txt", "./test_ann")
{'test1.txt': './test_ann/test1.ann', 'test2.txt': './test_ann/test2.ann'}
```

### Use as spaCy pipeline
``` python
>>> from taxonerd import TaxoNERD
>>> taxonerd = TaxoNERD(prefer_gpu=True)
>>> nlp = taxonerd.load(model="en_core_eco_biobert")
>>> doc = nlp("Brown bears (Ursus arctos), which are widely distributed throughout the northern hemisphere, are recognised as opportunistic omnivore")
>>> doc.ents
(Brown bears, Ursus arctos)
>>> [tok.lemma_ for tok in doc]
['Brown', 'bear', '(', 'ursus', 'arcto', ')', ',', 'which', 'be', 'widely', 'distribute', 'throughout', 'the', 'northern', 'hemisphere', ',', 'be', 'recognise', 'as', 'opportunistic', 'omnivore']
```

More examples in our [demo Notebook](https://github.com/nleguillarme/taxonerd/blob/9f5b1e264ba129eeeda383aa8085605c8fa9b379/taxonerd-demo.ipynb).

## Extensions

* [Combining TaxoNERD with gazetteer-based NER for improved taxonomic entities recognition](https://github.com/nleguillarme/taxonerd/blob/a58808e5808d74e341d0d98bc64dfebd7a670b81/extensions/entity_ruler.ipynb)

## License

License: MIT

## Authors

TaxoNERD was written by [nleguillarme](https://github.com/nleguillarme/).
