import os
from typing import List, Dict, Tuple, Optional


# =============== 常量定义 ===============


global_count: int = 0
file_dic: Dict[str, bool] = {}


# =============== 类定义 ===============


class Error(Exception):
    pass


class Assoc:
    dic: Dict[str, "Assoc"] = {}
    lis: List[str] = []
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.facts: List[str] = []
        self.rules: List[str] = []
        self.been: bool = False


# =============== 基石函数 ===============


def consp(string: str) -> bool:
    return string[0] == '(' and string[-1] == ')'


def match_parens(cons: str) -> Dict[int, int]:
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


def get_val(ele: str, binds: Dict[str, str]) -> str:
    while ele in binds:
        ele = binds[ele]
    return ele


def change_vars(cons: str, binds: Optional[Dict[str, str]] = None) -> Tuple[str, Optional[Dict[str, str]]]:
    if binds is None:
        binds = {}
    global global_count

    lis = cons_to_list(cons)
    new_lis = []
    for ele in lis:
        if consp(ele):
            new_ele, binds = change_vars(ele, binds)
        elif ele.startswith('*'):
            if ele in binds:
                new_ele = binds[ele]
            else:
                new_ele = f"*x{global_count}"
                global_count += 1
                binds[ele] = new_ele
        else:
            new_ele = ele
        new_lis.append(new_ele)
    return list_to_cons(new_lis), binds


# =============== 底层函数 ===============


def init():
    global global_count, file_dic
    global_count = 0
    file_dic = {}
    Assoc.dic = {}
    Assoc.lis = []


def save(file: str) -> None:
    if not os.path.exists("save"):
        os.mkdir("save")
    
    with open(f"save\\{file}", 'w', encoding='utf-8') as f:
        f.write('\n'.join(Assoc.lis))


def load(file: str) -> None:
    if file_dic.get(file, False):
        return
    file_dic[file] = True

    if not os.path.exists(f"save\\{file}"):
        raise Error("no such file")
    
    with open(f"save\\{file}", encoding='utf-8') as f:
        for line in f.readlines():
            execute(line.strip())
    
    file_dic[file] = False


def match(cons1: str, cons2: str, binds: Optional[Dict[str, str]] = None) -> Optional[Dict[str, str]]:
    '''Remember to judge None and this func is not destructive'''

    if binds is None:
        binds = {}
    new_binds = binds.copy()

    lis1, lis2 = cons_to_list(cons1), cons_to_list(cons2)
    if len(lis1) != len(lis2):
        return None
    for ele1, ele2 in zip(lis1, lis2):
        if ele1 == ele2:
            continue
        elif ele1 in new_binds:
            cont1 = get_val(ele1, new_binds)
            if ele2 in new_binds:
                cont2 = get_val(ele2, new_binds)
                if cont1 != cont2:
                    return None
            else:
                if cont1 != ele2:
                    return None
        elif ele2 in new_binds:
            cont2 = get_val(ele2, new_binds)
            if ele1 != cont2:
                return None
        elif ele1.startswith('*'):
            new_binds[ele1] = ele2
        elif ele2.startswith('*'):
            new_binds[ele2] = ele1
        elif consp(ele1) and consp(ele2):
            new_binds = match(ele1, ele2, new_binds)
            if new_binds is None:
                return None
        else:
            return None
    return new_binds


def parse(sentence: str) -> str:
    cons = sentence
    return cons


def define(cons: str) -> None:
    if car(cons) == "if":
        head = car(cdr(cons))
        name = car(head)
        assoc = Assoc.dic.setdefault(name, Assoc(name))
        assoc.rules.append(cdr(cons))
    else:
        name = car(cons)
        assoc = Assoc.dic.setdefault(name, Assoc(name))
        assoc.facts.append(cons)


def prove(cons: str, binds: Optional[Dict[str, str]] = None) -> Optional[List[Dict[str, str]]]:
    '''Remember to judge None'''

    name = car(cons)
    binds_lis = []
    if name == "and":
        cons1, cons2 = car(cdr(cons)), car(cdr(cdr(cons)))
        new_binds_lis = prove(cons1, binds)
        if new_binds_lis is None:
            return None
        for new_binds in new_binds_lis:
            nnew_binds_lis = prove(cons2, new_binds)
            if nnew_binds_lis is not None:
                binds_lis.extend(nnew_binds_lis)
        return binds_lis if binds_lis else None
    elif name == "or":
        cons1, cons2 = car(cdr(cons)), car(cdr(cdr(cons)))
        new_binds_lis = prove(cons1, binds)
        if new_binds_lis is not None:
            binds_lis.extend(new_binds_lis)
        new_binds_lis = prove(cons2, binds)
        if new_binds_lis is not None:
            binds_lis.extend(new_binds_lis)
        return binds_lis if binds_lis else None
    elif name == "not":
        cons1 = car(cdr(cons))
        new_binds_lis = prove(cons1, binds)
        if new_binds_lis is None:
            return [binds] if binds is not None else None
        return None
    else:
        assoc = Assoc.dic.get(name, Assoc(name))
        if assoc.been:
            return None
        assoc.been = True

        for fact in assoc.facts:
            fact = change_vars(fact)[0]
            new_binds = match(cons, fact, binds)
            if new_binds is not None:
                binds_lis.append(new_binds)
        for rule in assoc.rules:
            rule = change_vars(rule)[0]
            head, body = car(rule), car(cdr(rule))
            new_binds = match(cons, head, binds)
            if new_binds is not None:
                new_binds_lis = prove(body, new_binds)
                if new_binds_lis is not None:
                    binds_lis.extend(new_binds_lis)
        
        assoc.been = False
        return binds_lis if binds_lis else None


def search(cons: str) -> Optional[List[Dict[str, str]]]:
    binds_lis = prove(cons)
    if binds_lis is None:
        print("no matches")
    else:
        args = cons_to_list(cdr(cons))
        for i in range(len(binds_lis)):
            binds = binds_lis[i]
            print(f"possible match{i+1}:")
            for arg in args:
                print(f"{arg}: {get_val(arg, binds)}")
            print()


# =============== 终端函数 ===============


def execute(sentence):
    cons = parse(sentence)
    if car(cons) == "define":
        if sentence not in Assoc.lis:
            define(car(cdr(cons)))
            Assoc.lis.append(sentence)
    elif car(cons) == "search":
        search(car(cdr(cons)))
    elif car(cons) == "save":
        save(car(cdr(cons)))
    elif car(cons) == "load":
        load(car(cdr(cons)))
    else:
        raise Error("execute: no such command")


def main():
    init()
    print()
    while True:
        try:
            sentence = input('> ').strip()
            if not sentence:
                continue
            if sentence.lower() in ["quit", "exit"]:
                break
            execute(sentence)
        except Error as e:
            print("Error: ")
            print(e)
    print()