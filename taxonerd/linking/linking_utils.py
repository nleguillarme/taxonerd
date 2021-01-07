from typing import List, Dict, NamedTuple, Optional, Set, Tuple, Union
import json
from pathlib import Path
from collections import defaultdict
import sqlite3

from .file_cache import cached_path
from scispacy.umls_semantic_type_tree import (
    UmlsSemanticTypeTree,
    construct_umls_tree_from_tsv,
)

from urllib.request import pathname2url
import os

import logging

logger = logging.getLogger(__name__)


class Entity(NamedTuple):

    concept_id: str
    canonical_name: str
    aliases: List[str]
    types: List[str] = []
    definition: Optional[str] = None

    def __repr__(self):

        rep = ""
        num_aliases = len(self.aliases)
        rep = rep + f"CUI: {self.concept_id}, Name: {self.canonical_name}\n"
        rep = rep + f"Definition: {self.definition}\n"
        rep = rep + f"TUI(s): {', '.join(self.types)}\n"
        if num_aliases > 10:
            rep = (
                rep
                + f"Aliases (abbreviated, total: {num_aliases}): \n\t {', '.join(self.aliases[:10])}"
            )
        else:
            rep = (
                rep + f"Aliases: (total: {num_aliases}): \n\t {', '.join(self.aliases)}"
            )
        return rep


class KnowledgeBase:
    """
    A class representing two commonly needed views of a Knowledge Base:
    1. A mapping from concept_id to an Entity NamedTuple with more information.
    2. A mapping from aliases to the sets of concept ids for which they are aliases.

    Parameters
    ----------
    file_path: str, required.
        The file path to the json/jsonl representation of the KB to load.
    """

    def __init__(self, file_path: Union[str, Path, Tuple] = None, prefix: str = ""):
        self.prefix = prefix
        if file_path is None:
            raise ValueError(
                "Do not use the default arguments to KnowledgeBase. "
                "Instead, use a subclass (e.g GbifKnowledgeBase) or pass a path to a kb."
            )

        file_path = cached_path(file_path)
        if type(file_path) is tuple:
            user_friendly_name = file_path[1]
            file_path = file_path[0]
        db_path = os.path.splitext(file_path)[0] + ".db"

        if not os.path.exists(db_path):
            logger.info(
                "File {} not found, create SQLite database from {}".format(
                    db_path, file_path
                )
            )
            self.conn = self.json_to_sqlite(file_path, db_path)

        self.conn = self.get_conn_to_db(db_path)

    def json_to_sqlite(self, file_path: str = None, db_path: str = None):
        if file_path.endswith("jsonl"):
            raw = (json.loads(line) for line in open(cached_path(file_path)))
        else:
            raw = json.load(open(cached_path(file_path)))

        alias_to_cuis = defaultdict(set)
        cui_to_entity = {}

        for concept in raw:
            unique_aliases = set(concept["aliases"])
            unique_aliases.add(concept["canonical_name"])
            for alias in unique_aliases:
                # alias_to_cuis[alias] = (
                #     set() if alias not in alias_to_cuis else alias_to_cuis[alias]
                # )
                alias_to_cuis[alias].add(concept["concept_id"])
            cui_to_entity[concept["concept_id"]] = Entity(**concept)

        alias_to_cuis: Dict[str, Set[str]] = {**alias_to_cuis}

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""CREATE TABLE alias_to_cuis (alias, cuis)""")
        entries = [(k, str(v)) for k, v in alias_to_cuis.items()]
        c.executemany("INSERT INTO alias_to_cuis VALUES (?,?)", entries)
        conn.commit()
        return conn

    def get_conn_to_db(self, file_path: str = None):
        dburi = "file:{}?mode=rw".format(pathname2url(file_path))
        conn = sqlite3.connect(dburi, uri=True)
        return conn

    def get_cuis_from_alias(self, alias):
        c = self.conn.cursor()
        c.execute("SELECT cuis FROM alias_to_cuis WHERE alias = '{}';".format(alias))
        return [self.prefix + c.fetchone()[0].strip("{}")]

    def get_cuis_from_aliases(self, aliases):
        c = self.conn.cursor()
        aliases_str = ["'{}'".format(alias) for alias in aliases]
        c.execute(
            "SELECT alias, cuis FROM alias_to_cuis WHERE alias IN ({});".format(
                ",".join(aliases_str)
            )
        )
        mentions_to_concepts: Dict[str, List[str]] = defaultdict(list)
        for x in c.fetchall():
            concept_ids = [self.prefix + t.strip() for t in x[1].strip("{}").split(",")]
            mentions_to_concepts[x[0]].extend(
                concept_ids
            )  # self.prefix + x[1].strip("{}"))
        return mentions_to_concepts


class KnowledgeBaseFactory:
    def get_kb(self, name=None):
        if name == "gbif_backbone":
            return GbifKnowledgeBase()
        elif name == "taxref":
            return TaxRefKnowledgeBase()
        else:
            raise ValueError(name)


class GbifKnowledgeBase(KnowledgeBase):
    def __init__(
        self,
        file_path=(
            "https://cloud.univ-grenoble-alpes.fr/index.php/s/dm8attDW7EsdBpp/download",
            "gbif_backbone_2019-09-06.jsonl",
        ),
        prefix="GBIF:",
    ):
        super().__init__(file_path, prefix)


class TaxRefKnowledgeBase(KnowledgeBase):
    def __init__(
        self,
        file_path=(
            "https://cloud.univ-grenoble-alpes.fr/index.php/s/B48pMS5DmjiiiAJ/download",
            "taxref_v13.jsonl",
        ),
        prefix="TAXREF:",
    ):
        super().__init__(file_path, prefix)
