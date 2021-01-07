"""
Taxonomic named entity recognition using deep models
"""
from setuptools import find_packages, setup

dependencies = [
    "click",
    "pandas>=0.24.2",
    "scispacy>=0.2.5",
    "spacy>=2.3.2",
    "textract",
]

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="taxonerd",
    version="v1.0.1",
    url="https://github.com/nleguillarme/taxonerd",
    license="MIT",
    author="Nicolas Le Guillarme",
    author_email="nicolas.leguillarme@univ-grenoble-alpes.fr",
    description="A deep neural model for taxonomic entity recognition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=dependencies,
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
