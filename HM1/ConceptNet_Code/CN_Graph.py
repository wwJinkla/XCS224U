"""
Wei Wu
Sept 3, 2020
XCS224U A1
"""

import json
import pathlib
import requests
import sys
import time
from ratelimit import limits, sleep_and_retry  # https://pypi.org/project/ratelimit/
from typing import List
from tqdm import tqdm

# Excluded "/r/ExternalUrl"
# https://github.com/commonsense/conceptnet5/wiki/Relations
RELATIONS = [
    "RelatedTo",
    "FormOf",
    "IsA",
    "PartOf",
    "HasA",
    "UsedFor",
    "CapableOf",
    "AtLocation",
    "Causes",
    "HasSubevent",
    "HasFirstSubevent",
    "HasLastSubevent",
    "HasPrerequisite",
    "HasProperty",
    "MotivatedByGoal",
    "ObstructedBy",
    "Desires",
    "CreatedBy",
    "Synonym",
    "Antonym",
    "DistinctFrom",
    "DerivedFrom",
    "SymbolOf",
    "DefinedAs",
    "MannerOf",
    "LocatedNear",
    "HasContext",
    "SimilarTo",
    "MadeOf",
    "ReceivesAction",
    "EtymologicallyRelatedTo",
    "EtymologicallyDerivedFrom",
    "CausesDesire",
]


class CN_Graph:
    """
    Knowledge graph builder for ConceptNet5 using its Web API: https://github.com/commonsense/conceptnet5/wiki/API
    """

    def __init__(self, vocab: List):
        self.vocab = vocab

    @staticmethod
    def load(file_path):
        file = pathlib.Path(file_path)
        if not file.exists():
            return {}
        with open(file, "r") as f:
            return {key: set(value) for key, value in json.load(f).items()}

    @staticmethod
    def save(graph, file_path):
        graph = {key: list(value) for key, value in graph.items()}
        with open(file_path, "w") as outfile:
            json.dump(graph, outfile)

    @sleep_and_retry
    @limits(calls=1, period=1)
    def __request(self, word):
        url = f"http://api.conceptnet.io/c/en/{word}"
        response = requests.get(url)
        return response

    def build_graph(self):
        graph = {}
        for word in tqdm(self.vocab):
            graph[word] = set()
            response = self.__request(word)
            edges = response.json().get("edges", [])
            if len(edges) == 0:
                continue
            for edge in edges:
                if edge["rel"]["label"] in RELATIONS:
                    end = edge["end"]["label"]
                    if end != word and end in self.vocab:
                        graph[word].add(end)

        return graph
