from typing import List, Optional


class Error(Exception):
    pass


class Assoc:
    def __init__(self, name: str,
                 fact: Optional[list] = None,
                 defi: Optional[list] = None,
                 been: bool = False) -> None:
        self.name = name
        if fact is None:
            fact = []
        self.fact = fact
        if defi is None:
            defi = []
        self.defi = defi
        self.been = been


def match(cons1: str, cons2: str) -> Optional[dict]:
    pass


def parse(sentence: str) -> str:
    pass


def define(cons: str):
    pass


def search(cons: str) -> Optional[List[dict]]:
    pass