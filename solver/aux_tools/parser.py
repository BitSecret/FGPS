import copy
from sympy import sin, cos, tan, sqrt, pi, Float, Integer
from symbolic_solver.aux_tools.utils import number_round


class FormalLanguageParser:
    @staticmethod
    def _parse_one_predicate(s, make_vars=False):
        """
        parse s to get predicate, para, and structural msg.
        >> _parse_one_predicate('Predicate(ABC)')
        ('Predicate', ['A', 'B', 'C'], [3])
        >> _parse_one_predicate('Predicate(ABC, DE)', True)
        ('Predicate', ['a', 'b', 'c', 'd', 'e'], [3, 2])
        """
        predicate_name, para = s.split("(")
        if make_vars:
            para = para.replace(")", "").lower()
        else:
            para = para.replace(")", "")

        if "," not in para:
            return predicate_name, list(para), [len(para)]
        para_len = []
        para = para.split(",")
        for item in para:
            para_len.append(len(item))
        return predicate_name, list("".join(para)), para_len

    @staticmethod
    def parse_predicate(predicate_GDL):
        """parse predicate_GDL to logic form."""
        parsed_GDL = {  # preset Construction
            "FixLength": predicate_GDL["Preset"]["FixLength"],
            "VariableLength": predicate_GDL["Preset"]["VariableLength"],
            "Construction": predicate_GDL["Preset"]["Construction"],
            "BasicEntity": predicate_GDL["Preset"]["BasicEntity"],
            "Entity": {},
            "Relation": {},
            "Attribution": {}
        }
        entities = predicate_GDL["Entity"]  # parse entity
        for item in entities:
            name, para, para_len = FormalLanguageParser._parse_one_predicate(item, True)
            parsed_GDL["Entity"][name] = {
                "vars": para,
                "para_len": para_len,
                "ee_check": FormalLanguageParser._parse_ee_check(entities[item]["ee_check"]),
                "multi": FormalLanguageParser._parse_multi(entities[item]["multi"]),
                "extend": FormalLanguageParser._parse_extend(entities[item]["extend"])
            }

        relations = predicate_GDL["Relation"]  # parse relation
        for item in relations:
            name, para, para_len = FormalLanguageParser._parse_one_predicate(item, True)
            if "fv_check" in relations[item]:
                parsed_GDL["Relation"][name] = {
                    "vars": para,
                    "para_len": para_len,
                    "ee_check": FormalLanguageParser._parse_ee_check(relations[item]["ee_check"]),
                    "fv_check": FormalLanguageParser._parse_fv_check(relations[item]["fv_check"]),
                    "multi": FormalLanguageParser._parse_multi(relations[item]["multi"]),
                    "extend": FormalLanguageParser._parse_extend(relations[item]["extend"])
                }
            else:
                parsed_GDL["Relation"][name] = {
                    "vars": para,
                    "para_len": para_len,
                    "ee_check": FormalLanguageParser._parse_ee_check(relations[item]["ee_check"]),
                    "multi": FormalLanguageParser._parse_multi(relations[item]["multi"]),
                    "extend": FormalLanguageParser._parse_extend(relations[item]["extend"])
                }

        attributions = predicate_GDL["Attribution"]  # parse attribution
        for item in attributions:
            name, para, para_len = FormalLanguageParser._parse_one_predicate(item, True)
            if "fv_check" in attributions[item]:
                parsed_GDL["Attribution"][name] = {
                    "vars": para,
                    "para_len": para_len,
                    "ee_check": FormalLanguageParser._parse_ee_check(attributions[item]["ee_check"]),
                    "fv_check": FormalLanguageParser._parse_fv_check(attributions[item]["fv_check"]),
                    "sym": attributions[item]["sym"],
                    "multi": FormalLanguageParser._parse_multi(attributions[item]["multi"])
                }
            else:
                parsed_GDL["Attribution"][name] = {
                    "vars": para,
                    "para_len": para_len,
                    "ee_check": FormalLanguageParser._parse_ee_check(attributions[item]["ee_check"]),
                    "sym": attributions[item]["sym"],
                    "multi": FormalLanguageParser._parse_multi(attributions[item]["multi"])
                }

        return parsed_GDL

    @staticmethod
    def _parse_ee_check(ee_check):
        """
        parse ee_check to logic form.
        >> _parse_ee_check(['Triangle(ABC)'])
        [['Triangle', ['a', 'b', 'c']]]
        >> _parse_ee_check(['Line(AO)', 'Line(CO)'])
        [['Line', ['a', 'o']], ['Line', ['c', 'o']]]
        """
        results = []
        for item in ee_check:
            name, item_para, _ = FormalLanguageParser._parse_one_predicate(item, True)
            results.append([name, item_para])
        return results

    @staticmethod
    def _parse_fv_check(fv_check):
        """
        parse fv_check to logic form.
        >> _parse_fv_check(['O,AB,CD'])
        ['01234']
        >> _parse_fv_check(['AD,ABC', 'AB,ABC', 'AC,ABC'])
        ['01023', '01012', '01021']
        """
        results = []
        for item in fv_check:
            checked = []
            result = []
            for i in item.replace(",", ""):
                if i not in checked:
                    checked.append(i)
                result.append(str(checked.index(i)))
            results.append("".join(result))
        return results

    @staticmethod
    def _parse_multi(multi):
        """
        parse multi to logic form.
        >> _parse_multi(['BCA', 'CAB'])
        [['b', 'c', 'a'], ['c', 'a', 'b']]
        >> _parse_multi(['M,BA'])
        [['m', 'b', 'a']]
        """
        return [list(parsed_multi.replace(",", "").lower()) for parsed_multi in multi]

    @staticmethod
    def _parse_extend(extend_items):
        """
        parse extend to logic form.
        >> _parse_extend(['Equal(MeasureOfAngle(AOC),90)'])
        [['Equal', [['MeasureOfAngle', ['a', 'o', 'c']], '90']]]
        >> _parse_extend(['Perpendicular(AB,CB)', 'IsAltitude(AB,ABC)'])
        [['Perpendicular', ['a', 'b', 'c', 'b']], ['IsAltitude', ['a', 'b', 'a', 'b', 'c']]]
        """
        results = []
        for extend in extend_items:
            if extend.startswith("Equal"):
                parsed_equal, _ = FormalLanguageParser._parse_equal_predicate(extend, True)
                results.append(parsed_equal)
            else:
                extend_name, extend_para, _ = FormalLanguageParser._parse_one_predicate(extend, True)
                results.append([extend_name, extend_para])
        return results

    @staticmethod
    def parse_theorem(theorem_GDL, parsed_predicate_GDL):
        """parse theorem_GDL to logic form."""
        parsed_GDL = {}

        for theorem_name in theorem_GDL:
            name, para, para_len = FormalLanguageParser._parse_one_predicate(theorem_name, True)
            p1 = set(para)

            body = {}
            branch_count = 1
            for branch in theorem_GDL[theorem_name]:
                raw_premise_GDL = [theorem_GDL[theorem_name][branch]["premise"]]
                parsed_premise, paras_list = FormalLanguageParser._parse_premise(raw_premise_GDL)
                raw_theorem_GDL = theorem_GDL[theorem_name][branch]["conclusion"]
                parsed_conclusion, paras = FormalLanguageParser._parse_conclusion(raw_theorem_GDL)

                p2 = set(paras)
                if len(p2 - p1) > 0:
                    e_msg = "Theorem GDL definition error in <{}>.".format(theorem_name)
                    raise Exception(e_msg)

                for i in range(len(parsed_premise)):
                    p2 = set(paras_list[i])
                    if len(p2 - p1) > 0 or len(p1 - p2) > 0:
                        e_msg = "Theorem GDL definition error in <{}>.".format(theorem_name)
                        raise Exception(e_msg)
                    body[branch_count] = parsed_premise[i]
                    body[branch_count].update(parsed_conclusion)
                    branch_count += 1

            parsed_GDL[name] = {
                "vars": para,
                "para_len": para_len,
                "body": body
            }

        for predicate in parsed_predicate_GDL["Entity"]:
            conclusions = copy.copy(parsed_predicate_GDL["Entity"][predicate]["extend"])
            for multi in parsed_predicate_GDL["Entity"][predicate]["multi"]:
                conclusions.append([predicate, multi])
            if len(conclusions) == 0:
                continue

            name = predicate[0].lower()
            for i in range(1, len(predicate)):
                if predicate[i].isupper():
                    name += "_{}".format(predicate[i].lower())
                else:
                    name += predicate[i]
            name += "_definition"  # multi 是不是也要加进来？

            parsed_GDL[name] = {
                "vars": parsed_predicate_GDL["Entity"][predicate]["vars"],
                "para_len": parsed_predicate_GDL["Entity"][predicate]["para_len"],
                "body": {
                    "1": {
                        "products": [[predicate, parsed_predicate_GDL["Entity"][predicate]["vars"]]],
                        "logic_constraints": [],
                        "algebra_constraints": [],
                        "attr_in_algebra_constraints": [],
                        "conclusions": conclusions,
                        "attr_in_conclusions": []
                    }
                }
            }

        for predicate in parsed_predicate_GDL["Relation"]:
            conclusions = copy.copy(parsed_predicate_GDL["Relation"][predicate]["extend"])
            for multi in parsed_predicate_GDL["Relation"][predicate]["multi"]:
                conclusions.append([predicate, multi])
            if len(conclusions) == 0:
                continue

            name = predicate[0].lower()
            for i in range(1, len(predicate)):
                if predicate[i].isupper():
                    name += "_{}".format(predicate[i].lower())
                else:
                    name += predicate[i]
            name += "_definition"

            parsed_GDL[name] = {
                "vars": parsed_predicate_GDL["Relation"][predicate]["vars"],
                "para_len": parsed_predicate_GDL["Relation"][predicate]["para_len"],
                "body": {
                    "1": {
                        "products": [[predicate, parsed_predicate_GDL["Relation"][predicate]["vars"]]],
                        "logic_constraints": [],
                        "algebra_constraints": [],
                        "attr_in_algebra_constraints": [],
                        "conclusions": conclusions,
                        "attr_in_conclusions": []
                    }
                }
            }
        return parsed_GDL

    @staticmethod
    def _parse_premise(premise_GDL):
        """
        Convert geometric logic statements into disjunctive normal forms.
        A&(B|C) ==> A&B|A&C ==> [[A, B], [A, C]]
        >> _parse_premise(['Perpendicular(AO,CO)&(Collinear(OBC)|Collinear(OCB))'])
        [[['Perpendicular', ['a', 'o', 'c', 'o']], ['Collinear', ['o', 'b', 'c']]]
         [['Perpendicular', ['a', 'o', 'c', 'o']], ['Collinear', ['o', 'c', 'b']]]]
        """
        update = True
        while update:
            expanded = []
            update = False
            for item in premise_GDL:
                if "|" not in item:
                    expanded.append(item)
                else:
                    update = True
                    left_index = 0
                    or_index = item.index("|")
                    right_index = -1

                    count = 0
                    for i in range(1, len(item)):
                        if item[or_index - i] == ")":
                            count -= 1
                        elif item[or_index - i] == "(":
                            count += 1
                        if count == 1:
                            left_index = or_index - i
                            break
                    if left_index == 0:
                        head = ""
                    else:
                        head = item[0:left_index]

                    count = 0
                    for i in range(1, len(item)):
                        if item[or_index + i] == "(":
                            count -= 1
                        elif item[or_index + i] == ")":
                            count += 1
                        if count == 1:
                            right_index = or_index + i
                            break
                    if right_index == len(item) - 1:
                        tail = ""
                    else:
                        tail = item[right_index + 1:len(item)]

                    bodies = item[left_index + 1:right_index]
                    if "&(" not in bodies:
                        bodies = bodies.split("|")
                    else:
                        bodies = bodies.split("|", num=1)
                    for body in bodies:
                        expanded.append(head + body + tail)
            premise_GDL = expanded

        paras_list = []
        for i in range(len(premise_GDL)):  # listing
            premise_GDL[i] = premise_GDL[i].split("&")
            attrs = []
            paras = []
            for j in range(len(premise_GDL[i])):
                if "Equal" in premise_GDL[i][j]:
                    premise_GDL[i][j], eq_attrs = FormalLanguageParser._parse_equal_predicate(premise_GDL[i][j], True)
                    attrs += eq_attrs
                    for attr, para in eq_attrs:
                        paras += list(para)
                else:
                    predicate, para, _ = FormalLanguageParser._parse_one_predicate(premise_GDL[i][j], True)
                    premise_GDL[i][j] = [predicate, para]
                    paras += para

            product = []
            logic_constraint = []
            algebra_constraint = []
            existing_paras = set()
            for j in range(len(premise_GDL[i])):
                if premise_GDL[i][j][0] == "Equal":
                    algebra_constraint.append(premise_GDL[i][j])
                elif len(set(premise_GDL[i][j][1]) - existing_paras) == 0:
                    logic_constraint.append(premise_GDL[i][j])
                else:
                    existing_paras = existing_paras | set(premise_GDL[i][j][1])
                    product.append(premise_GDL[i][j])
            premise_GDL[i] = {
                "products": product,
                "logic_constraints": logic_constraint,
                "algebra_constraints": algebra_constraint,
                "attr_in_algebra_constraints": [[attr, list(para)] for attr, para in set(attrs)]
            }
            paras_list.append(paras)

        return premise_GDL, paras_list

    @staticmethod
    def _parse_conclusion(conclusion_GDL):
        """
        parse conclusion to logic form.
        >> _parse_conclusion(['Similar(ABC,ADE)'])
        [['Similar', ['a', 'b', 'c', 'a', 'd', 'e']]]
        """
        paras = []
        attrs = []
        for i in range(len(conclusion_GDL)):
            if "Equal" in conclusion_GDL[i]:
                conclusion_GDL[i], eq_attrs = FormalLanguageParser._parse_equal_predicate(conclusion_GDL[i], True)
                attrs += eq_attrs
                for attr, para in eq_attrs:
                    paras += list(para)
            else:
                predicate, para, _ = FormalLanguageParser._parse_one_predicate(conclusion_GDL[i], True)
                conclusion_GDL[i] = [predicate, para]
                paras += para

        parsed_conclusion_GDL = {
            "conclusions": conclusion_GDL,
            "attr_in_conclusions": [[attr, list(para)] for attr, para in set(attrs)]
        }
        return parsed_conclusion_GDL, paras

    @staticmethod
    def parse_problem(problem_CDL):
        """parse problem_CDL to logic form."""
        parsed_CDL = {
            "id": problem_CDL["problem_id"],
            "annotation": problem_CDL["annotation"],
            "cdl": {
                "construction_cdl": problem_CDL["construction_cdl"],
                "text_cdl": problem_CDL["text_cdl"],
                "image_cdl": problem_CDL["image_cdl"],
                "goal_cdl": problem_CDL["goal_cdl"]
            },
            "parsed_cdl": {
                "construction_cdl": [],
                "text_and_image_cdl": [],
                "goal": {},
            }
        }
        for fl in problem_CDL["construction_cdl"]:
            predicate, para = fl.split("(")
            para = para.replace(")", "")
            if predicate == "Shape":
                parsed_CDL["parsed_cdl"]["construction_cdl"].append([predicate, para.split(",")])
            elif predicate == "Collinear":
                parsed_CDL["parsed_cdl"]["construction_cdl"].append([predicate, list(para)])
            elif predicate == "Cocircular":
                parsed_CDL["parsed_cdl"]["construction_cdl"].append([predicate, list(para.replace(",", ""))])
            else:
                e_msg = "The predicate <{}> should not appear in construction_cdl.".format(predicate)
                raise Exception(e_msg)

        for fl in problem_CDL["text_cdl"] + problem_CDL["image_cdl"]:
            if fl.startswith("Equal"):
                parsed_equal, _ = FormalLanguageParser._parse_equal_predicate(fl)
                parsed_CDL["parsed_cdl"]["text_and_image_cdl"].append(parsed_equal)
            else:
                predicate, para, _ = FormalLanguageParser._parse_one_predicate(fl)
                parsed_CDL["parsed_cdl"]["text_and_image_cdl"].append([predicate, para])

        if problem_CDL["goal_cdl"].startswith("Value"):
            parsed_CDL["parsed_cdl"]["goal"]["type"] = "value"
            parsed_goal, _ = FormalLanguageParser._parse_equal_predicate(problem_CDL["goal_cdl"])
            parsed_CDL["parsed_cdl"]["goal"]["item"] = parsed_goal
            parsed_CDL["parsed_cdl"]["goal"]["answer"] = problem_CDL["problem_answer"]
        elif problem_CDL["goal_cdl"].startswith("Equal"):
            parsed_CDL["parsed_cdl"]["goal"]["type"] = "equal"
            parsed_goal, _ = FormalLanguageParser._parse_equal_predicate(problem_CDL["goal_cdl"])
            parsed_CDL["parsed_cdl"]["goal"]["item"] = parsed_goal
        elif problem_CDL["goal_cdl"].startswith("Relation"):
            parsed_CDL["parsed_cdl"]["goal"]["type"] = "logic"
            predicate, para, _ = FormalLanguageParser._parse_one_predicate(
                problem_CDL["goal_cdl"].split("(", 1)[1])
            parsed_CDL["parsed_cdl"]["goal"]["item"] = predicate
            parsed_CDL["parsed_cdl"]["goal"]["answer"] = para

        return parsed_CDL

    @staticmethod
    def parse_theorem_seqs(theorem_seqs):
        """parse theorem_seqs to logic form."""
        results = []

        for theorem in theorem_seqs:
            if "(" not in theorem:
                results.append([theorem, None])
            else:
                name, para, _ = FormalLanguageParser._parse_one_predicate(theorem)
                results.append([name, para])

        return results

    @staticmethod
    def _parse_equal_predicate(s, make_vars=False):
        """
        Parse s to a Tree.
        >> _parse_equal_predicate('Equal(LengthOfLine(OA),LengthOfLine(OB))', True)
        ['Equal', [['LengthOfLine', ['o', 'a']], ['LengthOfLine', ['o', 'b']]]]
        >> _parse_equal_predicate('Equal(Length(AB),Length(CD))')
        ['Equal', [[Length, ['A', 'B']], [Length, ['C', 'D']]]]
        """
        attrs = []
        i = 0
        j = 0
        stack = []
        while j < len(s):
            if s[j] == "(":
                stack.append(s[i:j])
                stack.append(s[j])
                i = j + 1

            elif s[j] == ",":
                if i < j:
                    stack.append(s[i: j])
                    i = j + 1
                else:
                    i = i + 1

            elif s[j] == ")":
                if i < j:
                    stack.append(s[i: j])
                    i = j + 1
                else:
                    i = i + 1

                paras = []
                while stack[-1] != "(":
                    paras.append(stack.pop())
                stack.pop()  # pop '('
                predicate = stack.pop()
                if predicate in EquationParser.operator_predicate or \
                        predicate in ["Value", "Equal", "Relation"]:  # not attribution
                    stack.append([predicate, paras[::-1]])
                else:  # attribution
                    paras = list("".join(paras[::-1]).lower() if make_vars else "".join(paras[::-1]))
                    stack.append([predicate, paras])
                    attrs.append((predicate, tuple(paras)))

            j = j + 1

        if len(stack) > 1:
            e_msg = "Sym stack not empty. Miss ')' in {}?.".format(s)
            raise Exception(e_msg)
        return stack.pop(), attrs


class EquationParser:
    operator_predicate = ["Add", "Sub", "Mul", "Div", "Pow", "Mod", "Sqrt", "Sin", "Cos", "Tan"]
    operator = ["+", "-", "*", "/", "^", "@", "#", "$", "√", "%", "{", "}", "~"]
    stack_priority = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3, "%": 3, "√": 4,
                      "@": 4, "#": 4, "$": 4,
                      "{": 0, "}": None, "~": 0,
                      }
    outside_priority = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3, "%": 3, "√": 4,
                        "{": 5, "}": 0,
                        "@": 4, "#": 4, "$": 4, "~": 0}

    @staticmethod
    def get_equation_from_tree(problem, tree, replaced=False, letters=None):
        """
        Trans expr_tree to symbolic algebraic expression.
        >> get_expr_from_tree(problem, [['LengthOfLine', ['a', 'b']], '2*x-14'], True, {'a': 'Z', 'b': 'X'})
        - 2.0*f_x + l_zx + 14.0
        >> get_expr_from_tree(problem, [['LengthOfLine', ['Z', 'X']], '2*x-14'])
        - 2.0*f_x + l_zx + 14.0
        """
        left_expr = EquationParser.get_expr_from_tree(problem, tree[0], replaced, letters)
        if left_expr is None:
            return None
        right_expr = EquationParser.get_expr_from_tree(problem, tree[1], replaced, letters)
        if right_expr is None:
            return None
        return left_expr - right_expr

    @staticmethod
    def get_expr_from_tree(problem, tree, replaced=False, letters=None):
        """
        Recursively trans expr_tree to symbolic algebraic expression.
        :param problem: class <Problem>.
        :param tree: An expression in the form of a list tree.
        :param replaced: Optional. Set True when tree's item is expressed by vars.
        :param letters: Optional. Letters that will replace vars. Dict = {var: letter}.
        >> get_expr_from_tree(problem, ['LengthOfLine', ['T', 'R']])
        l_tr
        >> get_expr_from_tree(problem, ['Add', [['LengthOfLine', ['Z', 'X']], '2*x-14']])
        2.0*f_x + l_zx - 14.0
        >> get_expr_from_tree(problem, ['Sin', [['MeasureOfAngle', ['a', 'b', 'c']]]],
                              True, {'a': 'X', 'b': 'Y', 'c': 'Z'})
        sin(pi*m_zxy/180)
        """
        if not isinstance(tree, list):  # expr
            return EquationParser._parse_expr(problem, tree)
        if tree[0] in problem.predicate_GDL["Attribution"]:  # attr
            if not replaced:
                return problem.get_sym_of_attr(tree[0], tuple(tree[1]))
            else:
                replaced_item = [letters[i] for i in tree[1]]
                return problem.get_sym_of_attr(tree[0], tuple(replaced_item))

        if tree[0] in ["Add", "Mul"]:  # operate
            expr_list = []
            for item in tree[1]:
                expr = EquationParser.get_expr_from_tree(problem, item, replaced, letters)
                if expr is None:
                    return None
                expr_list.append(expr)
            if tree[0] == "Add":
                result = 0
                for expr in expr_list:
                    result += expr
            else:
                result = 1
                for expr in expr_list:
                    result *= expr
            return result
        elif tree[0] in ["Sub", "Div", "Pow", "Mod"]:
            expr_left = EquationParser.get_expr_from_tree(problem, tree[1][0], replaced, letters)
            if expr_left is None:
                return None
            expr_right = EquationParser.get_expr_from_tree(problem, tree[1][1], replaced, letters)
            if expr_right is None:
                return None
            if tree[0] == "Sub":
                return expr_left - expr_right
            elif tree[0] == "Div":
                return expr_left / expr_right
            elif tree[0] == "Pow":
                return expr_left ** expr_right
            else:
                return expr_left % expr_right
        elif tree[0] in ["Sin", "Cos", "Tan", "Sqrt"]:
            expr = EquationParser.get_expr_from_tree(problem, tree[1][0], replaced, letters)
            if expr is None:
                return None
            if tree[0] == "Sin":
                return sin(expr * pi / 180)
            elif tree[0] == "Cos":
                return cos(expr * pi / 180)
            elif tree[0] == "Tan":
                return tan(expr * pi / 180)
            else:
                return sqrt(expr)
        else:
            e_msg = "Operator {} not defined, please check your expression.".format(tree[0])
            raise Exception(e_msg)

    @staticmethod
    def _parse_expr(problem, expr):
        """Parse the expression in <str> form into <symbolic> form"""
        i = 0
        expr_list = []
        for j in range(len(expr)):  # to list
            if expr[j] in EquationParser.operator:
                if i < j:
                    expr_list.append(expr[i:j])
                expr_list.append(expr[j])
                i = j + 1
        if i < len(expr):
            expr_list.append(expr[i:len(expr)])
        expr_list.append("~")

        expr_stack = []
        operator_stack = ["~"]  # stack bottom element

        i = 0
        while i < len(expr_list):
            unit = expr_list[i]
            if unit in EquationParser.operator:  # operator
                if EquationParser.stack_priority[operator_stack[-1]] < EquationParser.outside_priority[unit]:
                    operator_stack.append(unit)
                    i = i + 1
                else:
                    operator_unit = operator_stack.pop()
                    if operator_unit == "+":
                        expr_2 = expr_stack.pop()
                        expr_1 = expr_stack.pop()
                        expr_stack.append(expr_1 + expr_2)
                    elif operator_unit == "-":
                        expr_2 = expr_stack.pop()
                        expr_1 = 0 if len(expr_stack) == 0 else expr_stack.pop()
                        expr_stack.append(expr_1 - expr_2)
                    elif operator_unit == "*":
                        expr_2 = expr_stack.pop()
                        expr_1 = expr_stack.pop()
                        expr_stack.append(expr_1 * expr_2)
                    elif operator_unit == "/":
                        expr_2 = expr_stack.pop()
                        expr_1 = expr_stack.pop()
                        expr_stack.append(expr_1 / expr_2)
                    elif operator_unit == "^":
                        expr_2 = expr_stack.pop()
                        expr_1 = expr_stack.pop()
                        expr_stack.append(expr_1 ** expr_2)
                    elif operator_unit == "%":
                        expr_2 = expr_stack.pop()
                        expr_1 = expr_stack.pop()
                        expr_stack.append(expr_1 % expr_2)
                    elif operator_unit == "√":
                        expr_1 = expr_stack.pop()
                        expr_stack.append(sqrt(expr_1))
                    elif operator_unit == "@":  # sin
                        expr_1 = expr_stack.pop()
                        expr_stack.append(sin(expr_1))
                    elif operator_unit == "#":  # cos
                        expr_1 = expr_stack.pop()
                        expr_stack.append(cos(expr_1))
                    elif operator_unit == "$":  # tan
                        expr_1 = expr_stack.pop()
                        expr_stack.append(tan(expr_1))
                    elif operator_unit == "{":  # 只有unit为"}"，才能到达这个判断
                        i = i + 1
                    elif operator_unit == "~":  # 只有unit为"~"，才能到达这个判断，表示表达式处理完成
                        break
            else:  # symbol or number
                if unit == "π":  # pi
                    unit = pi
                elif unit.isalpha():  # free sym
                    unit = problem.get_sym_of_attr("Free", (unit,))
                elif "." in unit:  # float
                    unit = Float(unit)
                else:  # int
                    unit = Integer(unit)
                expr_stack.append(unit)
                i = i + 1

        if len(expr_stack) > 1:
            e_msg = "Wrong format: {}.".format(expr)
            raise Exception(e_msg)

        return number_round(expr_stack.pop())


class InverseParser:

    @staticmethod
    def inverse_parse_logic_to_cdl(problem):
        """Inverse parse conditions of logic form to CDL."""
        items = problem.condition.items
        steps = problem.condition.ids_of_step

        inverse_parsed_cdl = {}
        for step in sorted(list(steps)):
            if len(steps[step]) == 0:
                continue
            inverse_parsed_cdl[step] = []
            i = 0
            while i < len(steps[step]):
                _id = steps[step][i]
                predicate, item = items[_id][0], items[_id][1]

                if predicate in problem.predicate_GDL["Construction"] or \
                        predicate in problem.predicate_GDL["BasicEntity"]:  # skip preset
                    i += 1
                    continue

                result = InverseParser.inverse_parse_one(predicate, item, problem)
                inverse_parsed_cdl[step].append(result)

                if predicate in problem.predicate_GDL["Entity"]:  # remove duplicate representation
                    i += len(problem.predicate_GDL["Entity"][predicate]["multi"]) + 1
                elif predicate in problem.predicate_GDL["Relation"]:
                    i += len(problem.predicate_GDL["Relation"][predicate]["multi"]) + 1
                else:  # Equation
                    i += 1

        return inverse_parsed_cdl

    @staticmethod
    def inverse_parse_one(predicate, item, problem):
        """
        Inverse parse one condition of logic form to CDL.
        Called by <inverse_parse_logic_to_cdl>.
        """
        if predicate == "Equation":
            return InverseParser._inverse_parse_equation(item, problem)
        elif predicate in problem.predicate_GDL["Entity"]:
            return InverseParser.inverse_parse_logic(predicate, item, [1])
        elif predicate in problem.predicate_GDL["Relation"]:
            para_len = problem.predicate_GDL["Relation"][predicate]["para_len"]
            return InverseParser.inverse_parse_logic(predicate, item, para_len)
        else:
            return InverseParser._inverse_parse_preset(predicate, item)

    @staticmethod
    def inverse_parse_logic(predicate, item, para_len):
        """
        Inverse parse conditions of logic form to CDL.
        Note that this function also used by Solver for theorem inverse parse.
        >> inverse_parse_logic(Parallel, ('A', 'B', 'C', 'D'), [2, 2])
        'Parallel(AB,CD)'
        """
        if len(para_len) == 1:  # no need add ','
            return predicate + "(" + "".join(item) + ")"
        else:  # relation
            result = []
            i = 0
            for l in para_len:
                result.append("")
                for _ in range(l):
                    result[-1] += item[i]
                    i += 1
            return predicate + "(" + ",".join(result) + ")"

    @staticmethod
    def _inverse_parse_equation(item, problem):
        """
        Inverse parse conditions of logic form to CDL.
        Called by <inverse_parse_one>.
        >> _inverse_parse_one(ll_ac - ll_cd, equation)
        'Equation(ll_ac-ll_cd)'
        >> _inverse_parse_one(ll_ac - 1, equation)
        'LengthOfLine(AC)'
        """

        if len(item.free_symbols) == 1:
            sym = list(item.free_symbols)[0]
            if problem.condition.value_of_sym[sym] is not None and sym - problem.condition.value_of_sym[sym] == item:
                attr, items = problem.condition.attr_of_sym[sym]
                return attr + "(" + "".join(items[0]) + ")"

        return "Equation" + "(" + str(item).replace(" ", "") + ")"

    @staticmethod
    def _inverse_parse_preset(predicate, item):
        """
        Inverse parse conditions of logic form to CDL.
        Note that this function only inverse parse preset predicate.
        >> inverse_parse_logic(Line, ('A', 'B'))
        'Line(AB)'
        """
        if predicate == "Cocircular":
            if len(item) == 1:
                return "Cocircular({})".format(item[0])
            else:
                return "Cocircular({},{})".format(item[0], item[1:])
        elif predicate == "Shape":
            return "Shape({})".format(",".join(item))
        else:
            return "{}({})".format(predicate, "".join(item))
