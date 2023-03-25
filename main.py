import os
import re
from typing import List, Dict, Tuple, Optional


# =============== 常量定义 ===============


Cons = str
Binds = Dict[str, str]


# =============== 类定义 ===============


class Error(Exception):
    '''标准错误'''


class Exit(Exception):
    '''标准退出'''


class Assoc:
    '''逻辑事实及规则'''

    dic: Dict[str, "Assoc"] = {}
    __slots__ = ("name", "arg_num", "facts", "rules", "been")
    def __init__(self, name: str, arg_num: int) -> None:
        self.name = name
        self.arg_num = arg_num
        self.facts: List[Cons] = []
        self.rules: List[Cons] = []
        self.been: bool = False


class Expression:
    '''基本语法规则'''

    dic: Dict[str, "Expression"] = {}
    name_lis: List[str] = []
    __slots__ = ("name", "ptn_sent", "targ_cons", "ptn_cons", "targ_sent", "assoc_name_lis")
    def __init__(self, name: str,
            ptn_sent: re.Pattern, targ_cons: str,
            ptn_cons: re.Pattern, targ_sent: str) -> None:
        self.name = name
        self.ptn_sent = ptn_sent
        self.targ_cons = targ_cons
        self.ptn_cons = ptn_cons
        self.targ_sent = targ_sent
        self.assoc_name_lis: List[str] = []


class Operator:
    '''运算符语法规则'''

    dic: Dict[str, "Operator"] = {}
    level_lis: List[List["Operator"]] = []
    __slots__ = ("name", "left_num", "right_num", "level")
    def __init__(self, name: str, left_num: int, right_num: int, level: int) -> None:
        self.name = name
        self.left_num = left_num
        self.right_num = right_num
        self.level = level



# =============== 基石函数 ===============


def consp(string: str) -> bool:
    return string[0] == '(' and string[-1] == ')'


def match_parens(string: str) -> Dict[int, int]:
    matching = {}
    stack = []
    for i in range(len(string)):
        if string[i] == '(':
            stack.append(i)
        elif string[i] == ')':
            if not stack:
                raise Error("match_parens: Parentheses don't match")
            j = stack.pop()
            matching[i], matching[j] = j, i
    if stack:
        raise Error("match_parens: Parentheses don't match")
    return matching


def list_to_cons(lis: List[str]) -> Cons:
    return f"({' '.join(lis)})"


def cons_to_list(cons: Cons) -> List[str]:
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
            i = matching[i]
        else:
            last += cons[i]
        i += 1
    lis.append(last)
    return lis


def car(cons: Cons) -> str:
    return cons_to_list(cons)[0]


def cdr(cons: Cons) -> Cons:
    return list_to_cons(cons_to_list(cons)[1:])


def get_val(ele: str, binds: Binds) -> str:
    while ele in binds:
        ele = binds[ele]
    return ele


def change_vars(cons: Cons, binds: Optional[Binds] = None) -> Tuple[Cons, Optional[Binds]]:
    '''个性化变量名，以防出现意料外匹配'''

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
                new_ele = f"*@#:{global_count}"
                global_count += 1
                binds[ele] = new_ele
        else:
            new_ele = ele
        new_lis.append(new_ele)
    return list_to_cons(new_lis), binds


# =============== 底层函数 ===============


def init():
    global global_count, file_dic, cmd_lis
    global_count = 0
    file_dic = {}
    Assoc.dic = {}
    cmd_lis = []
    define("(= *x *x)")


def save(file: str) -> None:
    # 存档保存在save文件夹下
    if not os.path.exists("save"):
        os.mkdir("save")
    
    try:
        with open(f"save\\{file}", 'w', encoding='utf-8') as f:
            f.write('\n'.join(cmd_lis))
    except:
        raise Error("save: Fail to save")


def load(file: str) -> None:
    if file_dic.get(file, False):
        return
    file_dic[file] = True

    if not os.path.exists(f"save\\{file}"):
        raise Error("load: No such file")

    try:
        with open(f"save\\{file}", encoding='utf-8') as f:
            lines = f.readlines()
    except:
        raise Error("load: Fail to open file")

    for line in lines:
        execute(line.strip())
    file_dic[file] = False


def match(cons1: Cons, cons2: Cons, binds: Optional[Binds] = None) -> Optional[Binds]:
    '''非破坏性函数，不会改变原有binds'''

    if binds is None:
        binds = {}
    new_binds = binds.copy()

    lis1, lis2 = cons_to_list(cons1), cons_to_list(cons2)
    # 若两列表长度相同且每一对元素相等则匹配
    # 对每一对元素：
    #     若字面值相等则相等
    #     若其中一方为已绑定变量，匹配其值与另一方
    #     若其中一方为未绑定变量，建立新绑定
    #     若两方都为Cons，递归匹配
    #     否则不相等
    if len(lis1) != len(lis2):
        return None
    for ele1, ele2 in zip(lis1, lis2):
        if ele1 == ele2:
            continue
        elif ele1 in new_binds:
            cont1 = get_val(ele1, new_binds)
            new_binds = match(f"({cont1})", f"({ele2})", new_binds)
            if new_binds is None:
                return None
        elif ele2 in new_binds:
            cont2 = get_val(ele2, new_binds)
            new_binds = match(f"({ele1})", f"({cont2})", new_binds)
            if new_binds is None:
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
    return new_binds if new_binds else None


def standardlize(sentence: str) -> str:
    '''输入预处理'''

    sentence = ' ( '.join(sentence.split('('))
    sentence = ' ) '.join(sentence.split(')'))
    sentence = ' '.join(sentence.split())
    sentence = '('.join(sentence.split('( '))
    sentence = ')'.join(sentence.split(' )'))
    sentence = sentence.strip()
    return sentence


def parse(sentence: str) -> Cons:
    # 优先解析括号中语句
    matching = match_parens(sentence)
    new_sentence = ""
    i = 0
    while i < len(sentence):
        if sentence[i] == '(':
            new_sentence += parse(sentence[i+1:matching[i]])
            i = matching[i]
        else:
            new_sentence += sentence[i]
        i += 1
    sentence = new_sentence

    # 搜索每一个基本语法规则并转化为Cons
    for expr_name in Expression.name_lis:
        expr = Expression.dic[expr_name]
        while ans := re.search(expr.ptn_sent, sentence):
            temp_cons = expr.targ_cons.format(*ans.groups())
            assoc_name = car(temp_cons)
            # 若为新Assoc，划归该基本语法规则下
            if assoc_name not in Assoc.dic:
                expr.assoc_name_lis.append(assoc_name)
            sentence = sentence[:ans.start()] + temp_cons + sentence[ans.end():]

    # 将语句转化为原子列表。从高到低对每一层运算符优先级：
    #     扫描列表。若遇到该层运算符，据前置与后置参数数量生成Cons，若参数也为运算符则报语法错误
    atom_lis = cons_to_list(f"({sentence})")
    for level in range(len(Operator.level_lis)-1, -1, -1):
        new_atom_lis = []
        frame_op_name_lis = [operator.name for operator in Operator.level_lis[level]]
        i = 0
        while i < len(atom_lis):
            atom = atom_lis[i]
            if atom in frame_op_name_lis:
                operator = Operator.dic[atom]
                arg_lis = []
                for _ in range(operator.left_num):
                    try:
                        arg = new_atom_lis.pop()
                    except IndexError:
                        raise Error("parse: Wrong syntax")
                    if arg in Operator.dic.keys():
                        raise Error("parse: Wrong syntax")
                    arg_lis.insert(0, arg)
                for _ in range(operator.right_num):
                    try:
                        arg = atom_lis[i+1]
                    except IndexError:
                        raise Error("parse: Wrong syntax")
                    if arg in Operator.dic.keys():
                        raise Error("parse: Wrong syntax")
                    arg_lis.append(arg)
                    i += 1
                new_atom_lis.append(list_to_cons([atom, *arg_lis]))
            else:
                new_atom_lis.append(atom)
            i += 1
        atom_lis = new_atom_lis

    if len(atom_lis) != 1:
        raise Error("parse: Wrong syntax")
    cons = atom_lis[0]
    return cons


def define(cons: Cons) -> None:
    if car(cons) == "if":
        # 定义规则
        head = car(cdr(cons))
        assoc_name = car(head)
        arg_num = len(cons_to_list(head))-1
        assoc = Assoc.dic.setdefault(assoc_name, Assoc(assoc_name, arg_num))
        assoc.rules.append(cdr(cons))
    else:
        # 定义事实
        assoc_name = car(cons)
        arg_num = len(cons_to_list(cons))-1
        assoc = Assoc.dic.setdefault(assoc_name, Assoc(assoc_name, arg_num))
        assoc.facts.append(cons)


def prove(cons: Cons, binds: Optional[Binds] = None) -> Optional[List[Binds]]:
    name = car(cons)
    binds_lis = []
    if name == "and":
        # 取两参数中生成绑定不为空一方的绑定证明另一方
        cons1, cons2 = car(cdr(cons)), car(cdr(cdr(cons)))
        new_binds_lis1 = prove(cons1, binds)
        if new_binds_lis1 is not None:
            for new_binds in new_binds_lis1:
                nnew_binds_lis = prove(cons2, new_binds)
                if nnew_binds_lis is not None:
                    binds_lis.extend(nnew_binds_lis)
        else:
            new_binds_lis2 = prove(cons2, binds)
            if new_binds_lis2 is None:
                return None
            for new_binds in new_binds_lis2:
                nnew_binds_lis = prove(cons1, new_binds)
                if nnew_binds_lis is not None:
                    binds_lis.extend(nnew_binds_lis)
        return binds_lis if binds_lis else None
    elif name == "or":
        # 将两参数生成的绑定合并
        cons1, cons2 = car(cdr(cons)), car(cdr(cdr(cons)))
        new_binds_lis = prove(cons1, binds)
        if new_binds_lis is not None:
            binds_lis.extend(new_binds_lis)
        new_binds_lis = prove(cons2, binds)
        if new_binds_lis is not None:
            binds_lis.extend(new_binds_lis)
        return binds_lis if binds_lis else None
    elif name == "not":
        # 若参数生成空绑定，返回当前绑定
        cons1 = car(cdr(cons))
        new_binds_lis = prove(cons1, binds)
        if new_binds_lis is None:
            return [binds] if binds is not None else None
        return None
    else:
        arg_num = len(cons_to_list(cons))-1
        assoc = Assoc.dic.get(name, Assoc(name, arg_num))

        # 阻止递归调用规则以防陷入无限循环
        if assoc.been:
            return None
        assoc.been = True

        # 对每一个事实，生成对应绑定
        for fact in assoc.facts:
            fact = change_vars(fact)[0]
            new_binds = match(cons, fact, binds)
            if new_binds is not None:
                binds_lis.append(new_binds)

        # 对每一条规则，用head部分生成的绑定证明body部分
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


def search(sent: str) -> Optional[List[Binds]]:
    if consp(sent):
        cons = sent
    else:
        global global_count
        lis = [sent]
        for _ in range(Assoc.dic[sent].arg_num):
            lis.append(f"*@#:{global_count}")
            global_count += 1
        cons = list_to_cons(lis)

    binds_lis = prove(cons)
    if binds_lis is None:
        print("No matches")
    else:
        # 寻找该Assoc所属的基本语法规则，将Cons转化为语句
        assoc_name = car(cons)
        exprp = False
        for expr_name in Expression.name_lis:
            if assoc_name in Expression.dic[expr_name].assoc_name_lis:
                expr = Expression.dic[expr_name]
                exprp = True
                break

        output_pool = []
        for binds in binds_lis:
            new_atom_lis = []
            for atom in cons_to_list(cons):
                if atom in binds:
                    new_atom_lis.append(get_val(atom, binds))
                else:
                    new_atom_lis.append(atom)
            new_cons = list_to_cons(new_atom_lis)
            if new_cons not in output_pool:
                output_pool.append(new_cons)
                if exprp:
                    ans = re.match(expr.ptn_cons, new_cons)
                    print(expr.targ_sent.format(*ans.groups()))
                else:
                    print(new_cons)


# =============== 全局量定义 ===============


global_count: int = 0
cmd_lis: List[str] = []
file_dic: Dict[str, bool] = {}

Operator.dic["define"] = Operator("define", 0, 1, 0)
Operator.dic["search"] = Operator("search", 0, 1, 0)
Operator.dic["save"] = Operator("save", 0, 1, 0)
Operator.dic["load"] = Operator("load", 0, 1, 0)
Operator.dic["if"] = Operator("if", 1, 1, 1)
Operator.dic["and"] = Operator("and", 1, 1, 2)
Operator.dic["or"] = Operator("or", 1, 1, 2)
Operator.dic["not"] = Operator("not", 0, 1, 3)
for i in range(4):
    Operator.level_lis.append(list(filter(lambda x: x.level == i, Operator.dic.values())))

Expression.dic["is_not_of"] = Expression("is_not_of",
    re.compile(r'(\S+) is not (\S+) of (\S+)'), "(not ({1} {0} {2}))",
    re.compile(r''), "")
Expression.dic["is_not"] = Expression("is_not",
    re.compile(r'(\S+) is not (\S+)'), "(not ({1} {0}))",
    re.compile(r''), "")
Expression.dic["not_equals"] = Expression("not_equals",
    re.compile(r'(\S+) not equals (\S+)'), "(not (= {0} {1}))",
    re.compile(r''), "")
Expression.dic["is_of"] = Expression("is_of",
    re.compile(r'(\S+) is (\S+) of (\S+)'), "({1} {0} {2})",
    re.compile(r'\((\S+) (\S+) (\S+)\)'), "{1} is {0} of {2}")
Expression.dic["is"] = Expression("is",
    re.compile(r'(\S+) is (\S+)'), "({1} {0})",
    re.compile(r'\((\S+) (\S+)\)'), "{1} is {0}")
Expression.dic["equals"] = Expression("equals",
    re.compile(r'(\S+) equals (\S+)'), "(= {0} {1})",
    re.compile(r'\(= (\S+) (\S+)\)'), "{0} equals {1}")
Expression.name_lis = ["is_not_of", "is_not", "not_equals", "is_of", "is", "equals"]


# =============== 终端函数 ===============


def execute(sentence: str) -> None:
    if not sentence:
        return
    elif sentence in ["quit", "exit"]:
        raise Exit
    elif consp(sentence):
        sentence = standardlize(sentence)
        cons = sentence
    else:
        sentence = standardlize(sentence)
        cons = parse(sentence)

    command, cont = car(cons), car(cdr(cons))
    if command == "define":
        if sentence not in cmd_lis:
            define(cont)
            cmd_lis.append(sentence)
    elif command == "search":
        search(cont)
    elif command == "save":
        save(cont)
    elif command == "load":
        if sentence not in cmd_lis:
            load(cont)
            cmd_lis.append(sentence)
    else:
        raise Error("execute: No such command")


def main() -> None:
    '''顶层shell实现'''

    init()
    print()
    while True:
        try:
            sentence = input('> ').strip()
            execute(sentence)
        except Error as e:
            print("Error: ")
            print(e)
        except Exit as e:
            break
    print()


if __name__ == "__main__":
    main()