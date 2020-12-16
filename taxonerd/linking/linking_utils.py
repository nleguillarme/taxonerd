from typing import List, Dict, NamedTuple, Optional, Set
import json
from collections import defaultdict
import sqlite3

from scispacy.file_cache import cached_path
from scispacy.umls_semantic_type_tree import (
    UmlsSemanticTypeTree,
    construct_umls_tree_from_tsv,
)

from urllib.request import pathname2url
import os

import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("EntityLinker")


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


# DEFAULT_UMLS_PATH = "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/data/kbs/2020-10-09/umls_2020_aa_cat0129.jsonl"  # noqa
# DEFAULT_UMLS_TYPES_PATH = "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/data/umls_semantic_type_tree.tsv"


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

    def __init__(self, file_path: str = None, prefix: str = ""):
        self.prefix = prefix
        if file_path is None:
            raise ValueError(
                "Do not use the default arguments to KnowledgeBase. "
                "Instead, use a subclass (e.g UmlsKnowledgeBase) or pass a path to a kb."
            )

        db_path = os.path.splitext(file_path)[0] + ".db"
        try:
            db_path = cached_path(db_path)
            logger.debug("Found {}".format(db_path, file_path))
            self.conn = self.get_conn_to_db(db_path)
        except FileNotFoundError:
            logger.debug(
                "File {} not found, create SQLite database from {}".format(
                    db_path, file_path
                )
            )
            self.conn = self.json_to_sqlite(file_path, db_path)

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


# class UmlsKnowledgeBase(KnowledgeBase):
#     def __init__(
#         self,
#         file_path: str = DEFAULT_UMLS_PATH,
#         types_file_path: str = DEFAULT_UMLS_TYPES_PATH,
#     ):
#
#         super().__init__(file_path)
#
#         self.semantic_type_tree: UmlsSemanticTypeTree = construct_umls_tree_from_tsv(
#             types_file_path
#         )


class Gbif(KnowledgeBase):
    def __init__(self, file_path: str = "./gbif/gbif_backbone.jsonl", prefix="GBIF:"):
        super().__init__(file_path, prefix)


# class Mesh(KnowledgeBase):
#     def __init__(
#         self,
#         file_path: str = "https://ai2-s2-scispacy.s3-us-west-2.amazonaws.com/data/kbs/2020-10-09/mesh_2020.jsonl",  # noqa
#     ):
#         super().__init__(file_path)
#
#
# class GeneOntology(KnowledgeBase):
#     def __init__(
#         self,
#         file_path: str = "https://ai2-s2-scispacy.s3-us-west-2.amazonaws.com/data/kbs/2020-10-09/umls_2020_go.jsonl",  # noqa
#     ):
#         super().__init__(file_path)
#
#
# class HumanPhenotypeOntology(KnowledgeBase):
#     def __init__(
#         self,
#         file_path: str = "https://ai2-s2-scispacy.s3-us-west-2.amazonaws.com/data/kbs/2020-10-09/umls_2020_hpo.jsonl",  # noqa
#     ):
#         super().__init__(file_path)
#
#
# class RxNorm(KnowledgeBase):
#     def __init__(
#         self,
#         file_path: str = "https://ai2-s2-scispacy.s3-us-west-2.amazonaws.com/data/kbs/2020-10-09/umls_2020_rxnorm.jsonl",  # noqa
#     ):
#         super().__init__(file_path)
