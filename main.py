from typing import List, Dict, Tuple, Optional


# =============== 常量定义 ===============


assoc_dic: Dict[str, "Assoc"] = {}


# =============== 类定义 ===============


class Error(Exception):
    pass


class Assoc:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.facts: List[str] = []
        self.rules: List[Tuple[str]] = []
        self.been: bool = False


# =============== 基石函数 ===============


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
                raise Error("match_parens: parentheses don't match")
            j = stack.pop()
            matching[i], matching[j] = j, i
    if stack:
        raise Error("match_parens: parentheses don't match")
    return matching


def list_to_cons(lis: List[str]) -> str:
    return f"({' '.join(lis)})"


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


def car(cons: str) -> str:
    return cons_to_list(cons)[0]


def cdr(cons: str) -> str:
    return list_to_cons(cons_to_list(cons)[1:])


def get_val(ele: str, binds: dict) -> str:
    while ele in binds:
        ele = binds[ele]
    return ele


# =============== 底层函数 ===============


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
    return sentence


def def_fact(cons: str) -> None:
    assoc_name = car(cons)
    assoc = assoc_dic.setdefault(assoc_name, Assoc(assoc_name))
    assoc.facts.append(cdr(cons))


def def_rule(head: str, body: str) -> None:
    assoc_name = car(head)
    assoc = assoc_dic.setdefault(assoc_name, Assoc(assoc_name))
    assoc.rules.append((cdr(head), body))


def define(cons_lis: List[str]) -> None:
    if len(cons_lis) == 1:
        def_fact(cons_lis[0])
    elif len(cons_lis) == 2:
        def_rule(*cons_lis)
    else:
        raise Error("define: syntax is wrong")


def search(cons: str) -> Optional[List[dict]]:
    pass


# =============== 终端函数 ===============


def main():
    while True:
        try:
            sentence = input('>').strip()
            cons_lis = cons_to_list(parse(sentence))
            if cons_lis[0] == "define":
                define(cons_lis[1:])
            elif cons_lis[0] == "search":
                if len(cons_lis) != 2:
                    raise Error("main: syntax is wrong")
                search(cons_lis[1])
            else:
                raise Error("main: no such command")
        except Error as e:
            print("Error: ")
            print(e)