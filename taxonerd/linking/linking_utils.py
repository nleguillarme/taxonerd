from typing import List, Dict, NamedTuple, Optional, Set, Tuple, Union
import json
from pathlib import Path
from collections import defaultdict
import sqlite3
from .file_cache import cached_path
from urllib.request import pathname2url
import os
import logging

logger = logging.getLogger(__name__)


def escape_quotes(alias):
    alias = alias.replace("'", "''")
    alias = alias.replace('"', '""')
    return alias


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
        db_path = os.path.splitext(file_path)[0] + ".db"

        if file_path.endswith("jsonl"):
            raw = (
                json.loads(line)
                for line in open(cached_path(file_path), encoding="utf-8")
            )
        else:
            raw = json.load(open(cached_path(file_path), encoding="utf-8"))

        alias_to_cuis: Dict[str, Set[str]] = defaultdict(set)
        self.cui_to_entity: Dict[str, Entity] = {}

        for concept in raw:
            unique_aliases = set(concept["aliases"])
            # unique_aliases.add(concept["canonical_name"])
            for alias in unique_aliases:
                alias_to_cuis[alias].add(concept["concept_id"])
            self.cui_to_entity[concept["concept_id"]] = Entity(**concept)

        self.alias_to_cuis: Dict[str, Set[str]] = {**alias_to_cuis}

        if not os.path.exists(db_path):
            logger.info(
                "File {} not found, create SQLite database from {}".format(
                    db_path, file_path
                )
            )
            self.conn = self.json_to_sqlite(db_path)

        self.conn = self.get_conn_to_db(db_path)

    def json_to_sqlite(self, db_path: str = None):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""CREATE TABLE alias_to_cuis (alias, cuis)""")
        entries = [(k, str(v)) for k, v in self.alias_to_cuis.items()]
        c.executemany("INSERT INTO alias_to_cuis VALUES (?,?)", entries)
        conn.commit()
        return conn

    def get_conn_to_db(self, file_path: str = None):
        dburi = "file:{}?mode=rw".format(pathname2url(file_path))
        conn = sqlite3.connect(dburi, uri=True)
        return conn

    def get_cuis_from_alias(self, alias):
        c = self.conn.cursor()
        try:
            c.execute(
                "SELECT cuis FROM alias_to_cuis WHERE alias = '{}';".format(
                    escape_quotes(alias)
                )
            )
        except Exception as e:
            print(e, alias)
        return [self.prefix + ":" + c.fetchone()[0].strip("{}")]

    def get_cuis_from_aliases(self, aliases):
        c = self.conn.cursor()
        aliases_str = [
            "'{}'".format(escape_quotes(alias)) for alias in aliases
        ]  # Escape ' with ''
        c.execute(
            "SELECT alias, cuis FROM alias_to_cuis WHERE alias IN ({});".format(
                ",".join(aliases_str)
            )
        )
        mentions_to_concepts: Dict[str, List[str]] = defaultdict(list)
        for x in c.fetchall():
            concept_ids = [
                self.prefix + ":" + t.strip() for t in x[1].strip("{}").split(",")
            ]
            mentions_to_concepts[x[0]].extend(concept_ids)
        return mentions_to_concepts


class KnowledgeBaseFactory:

    def __init__(self):
        self.factory = {
            "gbif_backbone": GbifKnowledgeBase,
            "taxref": TaxRefKnowledgeBase,
            "ncbi_taxonomy": NCBIKnowledgeBase,
            # "ncbi_lite": NCBILiteKnowledgeBase(),
        }

    def get_kb(self, name_or_path=None):
        if name_or_path in self.factory:
            return self.factory[name_or_path]()
        else:
            path = Path(name_or_path)
            if path.exists() and path.is_dir():
                kb_file = list(path.glob("*.jsonl"))
                if len(kb_file) == 1:
                    return KnowledgeBase(file_path=kb_file[0], prefix=path.name.upper())
        logger.info(f"Cannot initialize KnowledgeBase with name or path {name_or_path}")
        return None


class GbifKnowledgeBase(KnowledgeBase):
    def __init__(
        self,
        file_path=(
            "https://cloud.univ-grenoble-alpes.fr/s/jpzMLYDLkG7ywSH/download",
            "gbif_backbone/gbif_backbone_20230828.jsonl",
        ),
        prefix="GBIF",
    ):
        super().__init__(file_path, prefix)


class TaxRefKnowledgeBase(KnowledgeBase):
    def __init__(
        self,
        file_path=(
            "https://cloud.univ-grenoble-alpes.fr/s/jPCMbGoDN8Pi6QP/download",
            "taxref/taxref_v17.jsonl",
        ),
        prefix="TAXREF",
    ):
        super().__init__(file_path, prefix)


class NCBIKnowledgeBase(KnowledgeBase):
    def __init__(
        self,
        file_path=(
            "https://cloud.univ-grenoble-alpes.fr/s/Sg487BjiSYkJqtC/download",
            "ncbi_taxonomy/ncbi_taxonomy_20240522.jsonl",
        ),
        prefix="NCBI",
    ):
        super().__init__(file_path, prefix)


# class NCBILiteKnowledgeBase(KnowledgeBase):
#     def __init__(
#         self,
#         file_path=(
#             "https://cloud.univ-grenoble-alpes.fr/index.php/s/cAmmpE6FxDxNBHj/download",
#             "ncbi_lite_2021_03_25.jsonl",
#         ),
#         prefix="NCBI",
#     ):
#         super().__init__(file_path, prefix)
