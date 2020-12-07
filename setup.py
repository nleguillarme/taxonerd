"""
Taxonomic named entity recognition using deep models
"""
from setuptools import find_packages, setup

dependencies = ["click", "pandas>=0.24.2", "scispacy>=0.2.5", "spacy>=2.3.2"]

setup(
    name="TaxoNERD",
    version="0.1.1",
    url="https://github.com/nleguillarme/taxonerd",
    license="MIT",
    author="Nicolas Le Guillarme",
    author_email="nicolas.leguillarme@univ-grenoble-alpes.fr",
    description="A deep neural model for taxonomic entity recognition",
    long_description=__doc__,
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
