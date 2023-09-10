import os
from solver.problem.problem import Problem
from solver.aux_tools.parser import GDLParser, CDLParser
from solver.aux_tools.parser import InverseParserM2F
from solver.core.engine import EquationKiller as EqKiller
from solver.core.engine import GeometryPredicateLogic as GeoLogic
from solver.aux_tools.output import get_used
from solver.aux_tools.utils import load_json, save_json
from collections import deque
from itertools import combinations
import time
import copy
from func_timeout import func_set_timeout
import random

path_gdl = "../../datasets/gdl/"
path_problems = "../../datasets/problems/"
path_raw_gdl = "../../utils/gdl/"
path_search = "../../utils/search/"


def get_p2t_map():
    if "p2t_map.json" in os.listdir(path_search):
        return load_json(path_search + "p2t_map.json")

    t_msg = {}
    gdl = load_json(path_raw_gdl + "theorem.json")["Theorems"]
    for theorem in gdl:
        t_name = theorem.split("(", 1)[0]
        t_msg[t_name] = [gdl[theorem]["category"], 0]

    for filename in os.listdir(path_problems):
        for theorem in load_json(path_problems + filename)["theorem_seqs"]:
            t_name = theorem.split("(", 1)[0]
            t_msg[t_name][1] += 1

    parsed_theorem_GDL = GDLParser.parse_theorem_gdl(
        load_json(path_gdl + "theorem_GDL.json"),
        GDLParser.parse_predicate_gdl(load_json(path_gdl + "predicate_GDL.json"))
    )

    p2t_map = {}
    for t_name in t_msg:
        if t_msg[t_name][1] == 0 or t_msg[t_name][0] == 3:  # skip no used and diff t
            continue
        for t_branch in parsed_theorem_GDL[t_name]["body"]:
            theorem_unit = parsed_theorem_GDL[t_name]["body"][t_branch]
            premises = list(theorem_unit["products"])
            premises += list(theorem_unit["logic_constraints"])
            premises += list(theorem_unit["attr_in_algebra_constraints"])
            for predicate, _ in premises:
                if predicate[0] == "~":  # skip oppose
                    continue
                if predicate not in p2t_map:
                    p2t_map[predicate] = [(t_name, t_branch)]
                elif (t_name, t_branch) not in p2t_map[predicate]:
                    p2t_map[predicate].append((t_name, t_branch))

    save_json(p2t_map, path_search + "p2t_map.json")
    return p2t_map


class Node:

    def __init__(self, base_problem, father, father_selection, pos, theorem_GDL, p2t_map):
        """
        Init forward search tree Node.
        :param base_problem: Instance of <solver.problem.Problem>.
        :param father: Father node.
        :param father_selection: ((t_name, t_branch, t_para), ((predicate, item, premise),)).
        :param pos: <tuple>, (depth, width, index).
        :param theorem_GDL: theorem GDL.
        :param p2t_map: msg problem-solving needed.
        """
        self.base_problem = base_problem
        self.theorem_GDL = theorem_GDL
        self.p2t_map = p2t_map

        self.father = father
        self.father_selection = father_selection  # apply father_selection then get current node
        self.pos = pos

        self.selections = []  # selections in current node
        self.last_step = 0

    def check_goal(self):
        """
        Rebuild and return problem.
        :return problem: rebuild problem.
        :return solved: True, False and None. Close current branch when set None.
        """
        applied_selections = []
        node = self.father
        while node is not None:
            if node.father_selection is not None:
                applied_selections.append(node.father_selection)
            node = node.father

        problem = Problem()  # rebuild problem
        problem.load_problem_by_copy(self.base_problem)
        for t_msg, conclusions in applied_selections:
            t_name, t_branch, t_para = t_msg
            theorem = InverseParserM2F.inverse_parse_logic(t_name, t_para, self.theorem_GDL[t_name]["para_len"])

            for predicate, item, premise in conclusions:
                problem.add(predicate, item, premise, theorem, skip_check=True)
            problem.step(theorem, 0)

        if self.father_selection is not None:  # apply current theorem selection
            self.last_step = problem.condition.step_count
            update = False
            t_msg, conclusions = self.father_selection
            t_name, t_branch, t_para = t_msg
            theorem = InverseParserM2F.inverse_parse_logic(t_name, t_para, self.theorem_GDL[t_name]["para_len"])

            for predicate, item, premise in conclusions:
                update = problem.add(predicate, item, premise, theorem, skip_check=True) or update
            problem.step(theorem, 0)

            if not update:  # close current branch if applied theorem no new condition
                return problem, None

        EqKiller.solve_equations(problem)  # solve eq & check_goal
        problem.check_goal()
        if problem.goal.solved:
            return problem, True
        return problem, False

    def get_children(self, problem):
        """
        Generate new theorem selection and build children node.
        Note that many operations swapping time for memory :(.
        :param problem: rebuild problems.
        :return nodes: <Node>.
        """
        unapplied_selections = []
        applied_selections = []
        node = self
        while node is not None:
            if node.father_selection is not None:
                applied_selections.append(node.father_selection)
            for selection in node.selections:
                if selection not in unapplied_selections and selection not in applied_selections:
                    unapplied_selections.append(selection)
            node = node.father

        self.selections = self.get_theorem_selection(problem)
        for i in range(len(self.selections))[::-1]:
            if self.selections[i] in unapplied_selections or self.selections[i] in applied_selections:
                self.selections.pop(i)

        nodes = []
        children_selections = unapplied_selections + self.selections
        for i in range(len(children_selections)):
            pos = (self.pos[0] + 1, len(children_selections), i + 1)
            nodes.append(Node(self.base_problem, self, children_selections[i], pos, self.theorem_GDL, self.p2t_map))

        return nodes

    def get_theorem_selection(self, problem):
        """
        Return theorem selections according to <self.last_step>.
        :return selections: <list> of ((t_name, t_branch, t_para), ((predicate, item, premise))).
        """
        selections = []
        added_selections = set()
        related_pres = []  # new added predicates
        related_eqs = []  # new added/updated equations

        for step in range(self.last_step, problem.condition.step_count):  # get related conditions
            for _id in problem.condition.ids_of_step[step]:
                if problem.condition.items[_id][0] == "Equation":
                    if problem.condition.items[_id][1] in related_eqs:
                        continue
                    related_eqs.append(problem.condition.items[_id][1])
                    for simp_eq in problem.condition.simplified_equation:
                        if simp_eq in related_eqs:
                            continue
                        if _id not in problem.condition.simplified_equation[simp_eq]:
                            continue
                        related_eqs.append(simp_eq)
                else:
                    if problem.condition.items[_id][0] not in self.p2t_map:
                        continue
                    if problem.condition.items[_id][0] in related_pres:
                        continue
                    related_pres.append(problem.condition.items[_id][0])

        new_selections = self.try_theorem_logic(problem, related_pres) + self.try_theorem_algebra(problem, related_eqs)
        # 下面代码啥意思？
        for selection in new_selections:
            _, conclusions = selection
            s = []
            for conclusion in conclusions:
                predicate, item, _ = conclusion
                s.append((predicate, item))
            s = tuple(s)
            if s not in added_selections:
                added_selections.add(s)
                selections.append(selection)

        return selections

    def try_theorem_logic(self, problem, related_pres):
        """
        Try a theorem and return can-added conclusions.
        :param problem: <Problem>, rebuild problem.
        :param related_pres: <list>, list of related predicates.
        :return selections: <list> of ((t_name, t_branch, t_para, t_timing), ((predicate, item, premise))).
        """
        theorem_logic = []  # [(theorem_name, theorem_branch)]
        for predicate in related_pres:
            for theorem in self.p2t_map[predicate]:
                if theorem in theorem_logic:
                    continue
                theorem_logic.append(theorem)

        selections = []
        for t_name, t_branch in theorem_logic:
            gpl = self.theorem_GDL[t_name]["body"][t_branch]
            results = GeoLogic.run(gpl, problem)  # get gpl reasoned result
            for letters, premise, conclusion in results:
                t_para = tuple([letters[i] for i in self.theorem_GDL[t_name]["vars"]])
                premise = tuple(premise)
                conclusions = []
                for predicate, item in conclusion:  # add conclusion
                    if problem.can_add(predicate, item, premise, t_name):
                        if predicate != "Equation":
                            item = tuple(item)
                        conclusions.append((predicate, item, premise))

                if len(conclusions) > 0:
                    selections.append(((t_name, t_branch, t_para), tuple(conclusions)))

        return selections

    def try_theorem_algebra(self, problem, related_eqs):
        """
        Try a theorem and return can-added conclusions.
        :param problem: <Problem>, rebuild problem.
        :param related_eqs: <list>, related equations.
        :return selections: <list> of ((t_name, t_branch, t_para, t_timing), ((predicate, item, premise))).
        """
        syms = EqKiller.get_minimum_syms(related_eqs, list(problem.condition.simplified_equation))
        paras_of_attrs = {}
        for sym in syms:
            attr, paras = problem.condition.attr_of_sym[sym]
            if attr not in self.p2t_map:
                continue

            if attr not in paras_of_attrs:
                paras_of_attrs[attr] = []

            for para in paras:
                if para in paras_of_attrs[attr]:
                    continue
                paras_of_attrs[attr].append(para)

        selections = []
        for related_attr in paras_of_attrs:
            related_paras = set(paras_of_attrs[related_attr])

            for t_name, t_branch in self.p2t_map[related_attr]:
                gpl = self.theorem_GDL[t_name]["body"][t_branch]  # run gdl
                r_ids, r_items, r_vars = GeoLogic.run_logic(gpl, problem)
                if len(r_ids) == 0:
                    continue

                new_ids = []
                new_items = []
                for i in range(len(r_ids)):  # filter related syms
                    letters = {}
                    for j in range(len(r_vars)):
                        letters[r_vars[j]] = r_items[i][j]
                    t_paras = set()
                    for t_attr, t_para in gpl["attr_in_algebra_constraints"]:
                        if t_attr != related_attr:
                            continue
                        t_paras.add(tuple([letters[p] for p in t_para]))
                    if len(related_paras & t_paras) > 0:
                        new_ids.append(r_ids[i])
                        new_items.append(r_items[i])

                r = GeoLogic.run_algebra((new_ids, new_items, r_vars), gpl, problem)  # check algebra constraints
                results = GeoLogic.make_conclusion(r, gpl, problem)
                for letters, premise, conclusion in results:
                    theorem_para = tuple([letters[i] for i in self.theorem_GDL[t_name]["vars"]])
                    premise = tuple(premise)
                    conclusions = []
                    for predicate, item in conclusion:  # add conclusion
                        if problem.can_add(predicate, item, premise, t_name):
                            if predicate != "Equation":
                                item = tuple(item)
                            conclusions.append((predicate, item, premise))

                    if len(conclusions) > 0:
                        selections.append(((t_name, t_branch, theorem_para), tuple(conclusions)))

        return selections


class ForwardSearcher:

    def __init__(self, predicate_GDL, theorem_GDL, method, max_depth, beam_size, p2t_map, debug=False):
        """
        Initialize Forward Searcher.
        :param predicate_GDL: predicate GDL.
        :param theorem_GDL: theorem GDL.
        :param method: <str>, "dfs", "bfs", "rs", "bs".
        :param max_depth: max search depth.
        :param beam_size: beam search size.
        :param p2t_map: <dict>, {predicate/attr: [(theorem_name, branch)]}, map predicate to theorem.
        :param debug: <bool>, set True when need print process information.
        """
        self.predicate_GDL = GDLParser.parse_predicate_gdl(predicate_GDL)
        self.theorem_GDL = GDLParser.parse_theorem_gdl(theorem_GDL, self.predicate_GDL)
        self.max_depth = max_depth
        self.beam_size = beam_size
        self.method = method
        self.debug = debug
        self.p2t_map = p2t_map

        self.problem = None
        self.stack = None

    def init_search(self, problem_CDL):
        """Initial problem by problem_CDL and build root Node."""
        self.problem = Problem()
        self.problem.load_problem_by_fl(self.predicate_GDL, CDLParser.parse_problem(problem_CDL))  # load problem
        EqKiller.solve_equations(self.problem)
        self.problem.step("init_problem", 0)  # save applied theorem and update step

        root = Node(self.problem, None, None, (1, 1, 1), self.theorem_GDL, self.p2t_map)
        self.stack = []
        self.stack.append(root)

    @func_set_timeout(150)
    def search(self):
        """
        Search problem and return search result.
        :return solved: <bool>, indicate whether problem solved or not.
        :return seqs: <list> of <str>, solved theorem sequences.
        """
        if self.method == "bfs":  # breadth-first search
            while len(self.stack) > 0:
                node = self.stack.pop(0)
                problem, solved = node.check_goal()
                if solved is None:  # not update, close search branch
                    continue
                if solved:  # solved, return result
                    _, seqs = get_used(problem)
                    return True, seqs
                else:  # continue search
                    for child_node in node.get_children(problem):
                        self.stack.append(child_node)
        elif self.method == "dfs":  # deep-first search
            while len(self.stack) > 0:
                node = self.stack.pop()
                problem, solved = node.check_goal()
                if solved is None:  # not update, close search branch
                    continue
                if solved:  # solved, return result
                    _, seqs = get_used(problem)
                    return True, seqs
                else:  # continue search
                    for child_node in node.get_children(problem):
                        self.stack.append(child_node)
        elif self.method == "rs":  # random search
            while len(self.stack) > 0:
                node = self.stack.pop(random.randint(0, len(self.stack) - 1))
                problem, solved = node.check_goal()
                if solved is None:  # not update, close search branch
                    continue
                if solved:  # solved, return result
                    _, seqs = get_used(problem)
                    return True, seqs
                else:  # continue search
                    for child_node in node.get_children(problem):
                        self.stack.append(child_node)
        else:  # beam search
            while len(self.stack) > 0:
                if len(self.stack) > self.beam_size:  # select branch with beam size
                    stack = []
                    for i in random.sample(range(len(self.stack)), self.beam_size):
                        stack.append(self.stack[i])
                    self.stack = stack

                new_stack = []
                for node in self.stack:  # expand all selected branch
                    problem, solved = node.check_goal()
                    if solved is None:  # not update, close search branch
                        continue
                    if solved:  # solved, return result
                        _, seqs = get_used(problem)
                        return True, seqs
                    else:  # continue search
                        for child_node in node.get_children(problem):
                            new_stack.append(child_node)

                self.stack = new_stack

        return False, None


def main():
    searcher = ForwardSearcher(
        load_json(path_gdl + "predicate_GDL.json"), load_json(path_gdl + "theorem_GDL.json"),
        method="bfs", max_depth=5, beam_size=5,
        p2t_map=get_p2t_map(), debug=True
    )
    while True:
        pid = input("pid:")
        searcher.init_search(load_json(path_problems + "{}.json".format(pid)))
        solved, seqs = searcher.search()
        print("pid: {}  solved: {}  seqs:{}\n".format(pid, solved, seqs))


if __name__ == '__main__':
    main()
