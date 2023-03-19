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


def consp(string: str) -> bool:
    return string[0] == '(' and string[-1] == ')'


def match_parens(cons: str) -> dict:
    matching = {}
    stack = []
    for i in range(len(cons)):
        if cons[i] == '(':
            stack.append(i)
        elif cons[i] == ')':
            if not stack:
                raise Error("parentheses don't match")
            j = stack.pop()
            matching[i], matching[j] = j, i
    if stack:
        raise Error("parentheses don't match")
    return matching


def cons_to_list(cons: str) -> List[str]:
    '''Remember to add blank between elements'''

    matching = match_parens(cons)
    lis = []

    last = ""
    i = 1
    while i < len(cons)-1:
        if cons[i] == ' ':
            lis.append(last)
            last = ""
        elif cons[i] == '(':
            last = cons[i:matching[i]+1]
            i = matching[i]+1
            continue
        else:
            last += cons[i]
        i += 1
    lis.append(last)
    return lis


def get_val(ele: str, binds: dict) -> str:
    while ele in binds:
        ele = binds[ele]
    return ele


def match(cons1: str, cons2: str, binds: Optional[dict] = None) -> Optional[dict]:
    if binds is None:
        binds = {}

    lis1, lis2 = cons_to_list(cons1), cons_to_list(cons2)
    if len(lis1) != len(lis2):
        return None
    for ele1, ele2 in zip(lis1, lis2):
        if ele1 != ele2:
            return None
        elif ele1 in binds:
            cont1 = get_val(ele1, binds)
            if ele2 in binds:
                cont2 = get_val(ele2, binds)
                if cont1 != cont2:
                    return None
            else:
                if cont1 != ele2:
                    return None
        elif ele2 in binds:
            cont2 = get_val(ele2, binds)
            if ele1 != cont2:
                return None
        elif ele1.startswith('*'):
            binds[ele1] = ele2
        elif ele2.startswith('*'):
            binds[ele2] = ele1
        elif consp(ele1) and consp(ele2):
            binds = match(ele1, ele2, binds)
            if binds is None:
                return None
        else:
            return None
    return binds


def parse(sentence: str) -> str:
    pass


def define(cons: str):
    pass


def search(cons: str) -> Optional[List[dict]]:
    pass