"""
Taxonomic named entity recognition using deep models
"""
from setuptools import find_packages, setup

install_requires = [
    "click<7.2.0,>=7.1.1",
    "pandas>=0.24.2",
    "scispacy==0.4.0",
    "spacy>=3.0.5,<3.1.0",
    "spacy-transformers>=1.0.2,<1.0.5",
    "textract>=1.6.3",
]

extras_require = {
    "cuda102": [
        "spacy[cuda102]>=3.0.5,<3.1.0",
        "spacy-transformers[cuda102]>=1.0.2,<1.0.5",
        "cupy-cuda102",
    ],
    "cuda110": [
        "spacy[cuda110]>=3.0.5,<3.1.0",
        "spacy-transformers[cuda110]>=1.0.2,<1.0.5",
        "cupy-cuda110",
    ],
    "cuda111": [
        "spacy[cuda111]>=3.0.5,<3.1.0",
        "spacy-transformers[cuda111]>=1.0.2,<1.0.5",
        "cupy-cuda111",
    ],
    "cuda112": [
        "spacy[cuda112]>=3.0.5,<3.1.0",
        "spacy-transformers[cuda112]>=1.0.2,<1.0.5",
        "cupy-cuda112",
    ],
}

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="taxonerd",
    version="v1.3.2",
    url="https://github.com/nleguillarme/taxonerd",
    license="MIT",
    author="Nicolas Le Guillarme",
    author_email="nicolas.leguillarme@univ-grenoble-alpes.fr",
    description="Deep neural models for taxonomic entity recognition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={"console_scripts": ["taxonerd = taxonerd.cli:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
