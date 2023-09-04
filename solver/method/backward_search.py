from solver.aux_tools.output import get_used
from solver.method.forward_search import Theorem
from collections import deque
from enum import Enum
from func_timeout import func_set_timeout
from solver.problem.problem import Problem
from solver.aux_tools.parser import GDLParser, CDLParser
from solver.aux_tools.parser import InverseParserM2F
from solver.core.engine import EquationKiller as EqKiller
from solver.aux_tools.utils import rough_equal
import time
from graphviz import Digraph
from itertools import permutations
import copy


class GoalFinder:

    def __init__(self, theorem_GDL, t_msg):
        self.theorem_GDL = theorem_GDL
        self.p2t_map = {}
        self.selected = ["midsegment_of_quadrilateral_property_length", "midsegment_of_quadrilateral_judgment_midpoint"]

        for t_name in theorem_GDL:
            # if t_name not in self.selected:
            #     continue
            if t_name in t_msg and (t_msg[t_name][1] == 0 or t_msg[t_name][0] == 3):  # skip no used and diff t
                continue

            for branch in theorem_GDL[t_name]["body"]:
                theorem_unit = theorem_GDL[t_name]["body"][branch]
                for predicate, _ in theorem_unit["conclusions"] + theorem_unit["attr_in_conclusions"]:
                    if predicate == "Equal":
                        continue
                    if predicate not in self.p2t_map:
                        self.p2t_map[predicate] = [(t_name, branch)]
                    elif (t_name, branch) not in self.p2t_map[predicate]:
                        self.p2t_map[predicate].append((t_name, branch))

    def find_all_sub_goals(self, predicate, item, problem):
        """return [(sub_goals, (t_name, t_para, t_branch))]"""
        theorem_and_para = {}  # {(t_name, t_branch): set(t_paras)}

        if predicate == "Equation":  # algebra goal
            attr_to_paras = {}
            for sym in EqKiller.get_minimum_syms([item], list(problem.condition.simplified_equation)):
                attr, paras = problem.condition.attr_of_sym[sym]
                if attr == "Free":
                    continue
                if attr not in attr_to_paras:
                    attr_to_paras[attr] = []
                for para in paras:
                    if para not in attr_to_paras[attr]:
                        attr_to_paras[attr].append(para)

            for attr in attr_to_paras:
                for t_name, t_branch in self.p2t_map[attr]:
                    if (t_name, t_branch) not in theorem_and_para:
                        theorem_and_para[(t_name, t_branch)] = set()
                    t_paras = []
                    for t_attr, attr_vars in self.theorem_GDL[t_name]["body"][t_branch]["attr_in_conclusions"]:
                        if attr != t_attr:
                            continue
                        t_vars = copy.copy(self.theorem_GDL[t_name]["vars"])
                        for para in attr_to_paras[attr]:
                            t_para = [v if v not in attr_vars else para[attr_vars.index(v)] for v in t_vars]
                            t_paras.append(t_para)
                    t_paras = GoalFinder.theorem_para_completion(
                        t_paras, problem.condition.get_items_by_predicate("Point"))
                    theorem_and_para[(t_name, t_branch)] |= t_paras
        else:  # logic goal
            for t_name, t_branch in self.p2t_map[predicate]:
                if (t_name, t_branch) not in theorem_and_para:
                    theorem_and_para[(t_name, t_branch)] = set()
                t_paras = set()

                for t_predicate, item_vars in self.theorem_GDL[t_name]["body"][t_branch]["conclusions"]:
                    if t_predicate != predicate:
                        continue
                    t_vars = copy.copy(self.theorem_GDL[t_name]["vars"])
                    t_para = [v if v not in item_vars else item[item_vars.index(v)] for v in t_vars]
                    t_paras.add(tuple(t_para))

                t_paras = GoalFinder.theorem_para_completion(
                    t_paras, problem.condition.get_items_by_predicate("Point"))

                theorem_and_para[(t_name, t_branch)] |= t_paras

        return GoalFinder.gen_sub_goals(self.theorem_GDL, theorem_and_para, problem)

    @staticmethod
    def theorem_para_completion(t_paras, points):
        """
        Replace free vars with points.
        >> theorem_para_completion([['a', 'R', 'S']], ['A', 'R', 'S'])
        >> [['A', 'R', 'S'], ['R', 'R', 'S'], ['S', 'R', 'S']]
        """
        points = [points[i][0] for i in range(len(points))]
        results = set()
        for t_para in t_paras:
            vacant_index = []
            for i in range(len(t_para)):
                if t_para[i].islower():
                    vacant_index.append(i)
            for per_para in permutations(points, len(vacant_index)):
                result = [t_para[i] if i not in vacant_index else per_para[vacant_index.index(i)]
                          for i in range(len(t_para))]
                results.add(tuple(result))
        return results

    @staticmethod
    def gen_sub_goals(theorem_GDL, theorem_and_para, problem):
        """
        Construct and return legitimate sub goal.
        :param theorem_GDL: parsed theorem_GDL.
        :param theorem_and_para: {(t_name, t_branch): t_paras}.
        :param problem: Class <Problem>.
        :return results: [(t_name, t_branch, t_para, sub_goals)].
        """
        results = []
        for t in theorem_and_para:
            t_name, t_branch = t
            t_vars = theorem_GDL[t_name]["vars"]
            for t_para in theorem_and_para[t]:
                letters = {}
                for j in range(len(t_vars)):
                    letters[t_vars[j]] = t_para[j]

                sub_goals = []
                passed = True
                for predicate, item_vars in theorem_GDL[t_name]["body"][t_branch]["products"]:
                    item = tuple(letters[i] for i in item_vars)
                    if not (problem.ee_check(predicate, item) and problem.fv_check(predicate, item)):
                        passed = False
                        break
                    sub_goals.append((predicate, item))
                if not passed:
                    continue

                for predicate, item_vars in theorem_GDL[t_name]["body"][t_branch]["logic_constraints"]:
                    item = tuple(letters[i] for i in item_vars)
                    if not (problem.ee_check(predicate, item) and problem.fv_check(predicate, item)):
                        passed = False
                        break
                    sub_goals.append((predicate, item))
                if not passed:
                    continue

                for _, tree in theorem_GDL[t_name]["body"][t_branch]["algebra_constraints"]:
                    eq = CDLParser.get_equation_from_tree(problem, tree, True, letters)
                    if eq is None:
                        passed = False
                        break
                    sub_goals.append(("Equation", eq))
                if not passed:
                    continue

                result = (t_name, t_branch, t_para, tuple(sub_goals))
                if result not in results:
                    results.append(result)

        return results


class NodeState(Enum):
    to_be_expanded = 1
    expanded = 2
    success = 3
    fail = 4


class Node:
    def __init__(self, super_node, problem, predicate, item, node_map, finder):
        """Init node and set node state."""
        self.state = NodeState.to_be_expanded
        self.super_node = super_node  # class <SuperNode>
        self.children = []  # list of class <SuperNode>
        self.children_t_msg = set()  # set of (t_name, t_branch, t_para)

        self.problem = problem
        self.predicate = predicate
        self.item = item
        self.premise = []

        self.finder = finder
        self.node_map = node_map

        if predicate == "Equation":  # process 1
            for sym in self.item.free_symbols:
                if sym not in node_map:
                    node_map[sym] = [self]
                else:
                    node_map[sym].append(self)
            if item == 0:
                self.state = NodeState.success
        else:
            if (predicate, item) not in node_map:
                node_map[(predicate, item)] = [self]
            else:
                node_map[(predicate, item)].append(self)

            if predicate in ["Point", "Line", "Arc", "Angle", "Polygon", "Circle", "Collinear", "Cocircular"] and \
                    item not in self.problem.condition.get_items_by_predicate(predicate):
                self.state = NodeState.fail

        self.check_goal()

    def check_state(self):  # process 3
        if self.state in [NodeState.success, NodeState.fail]:
            return

        update = False
        fail = True
        success = False
        for child in self.children:
            if child.state != NodeState.fail:
                fail = False
            if child.state == NodeState.success:
                success = True

        if success:
            update = self.check_goal() or update

        if fail and len(self.children) > 0 and self.predicate != "Equation":
            self.state = NodeState.fail
            update = True

        if update:
            self.super_node.check_state()

    def check_goal(self):  # process 1
        """Return update or not"""
        if self.state in [NodeState.success, NodeState.fail]:
            return False

        if self.predicate == "Equation":
            result, premise = EqKiller.solve_target(self.item, self.problem)
            if result is None:
                return False

            if rough_equal(result, 0):
                self.state = NodeState.success
                self.premise = premise
            else:
                self.state = NodeState.fail
        else:
            if self.item not in self.problem.condition.get_items_by_predicate(self.predicate):
                return False
            self.state = NodeState.success
            self.premise = [self.problem.condition.get_id_by_predicate_and_item(self.predicate, self.item)]

        return True

    def expand(self):  # process 1
        if self.state in [NodeState.success, NodeState.fail]:
            return False
        self.state = NodeState.expanded

        depth = self.super_node.pos[0] + 1
        results = self.finder.find_all_sub_goals(self.predicate, self.item, self.problem)
        for t_name, t_branch, t_para, sub_goals in results:
            if (t_name, t_branch, t_para) in self.children_t_msg:
                continue
            self.children_t_msg.add((t_name, t_branch, t_para))

            super_node = SuperNode(self, self.problem, (t_name, t_branch, t_para), depth, self.node_map, self.finder)
            self.children.append(super_node)
            super_node.add_nodes(sub_goals)


class SuperNode:
    snc = {}  # {depth: super_node_count}

    def __init__(self, father_node, problem, theorem, depth, node_map, finder):
        self.state = NodeState.to_be_expanded
        self.nodes = []  # list of class <Node>
        self.father_node = father_node  # class <Node>
        self.problem = problem
        self.theorem = theorem  # (t_name, t_branch, t_para)
        if depth not in SuperNode.snc:
            SuperNode.snc[depth] = 0
        self.pos = (depth, SuperNode.snc[depth] + 1)  # (depth, node_number)
        SuperNode.snc[depth] += 1
        self.node_map = node_map
        self.finder = finder

    def add_nodes(self, sub_goals):
        father_super_nodes = []  # ensure no ring
        if self.father_node is not None:
            father_super_nodes.append(self.father_node.super_node)
        while len(father_super_nodes) > 0:
            super_node = father_super_nodes.pop()
            if super_node.theorem == self.theorem:
                self.state = NodeState.fail
                self.father_node.check_state()
                return
            if super_node.father_node is not None:
                father_super_nodes.append(super_node.father_node.super_node)

        for predicate, item in sub_goals:
            node = Node(self, self.problem, predicate, item, self.node_map, self.finder)
            self.nodes.append(node)
            if node.state == NodeState.fail:
                break

        self.check_state()

    def check_state(self):  # process 2
        if self.state in [NodeState.success, NodeState.fail]:
            return

        for node in self.nodes:
            if node.state == NodeState.fail:
                self.state = NodeState.fail
                if self.father_node is not None:
                    self.father_node.check_state()
                return

        success = True
        for node in self.nodes:
            if node.state != NodeState.success:
                success = False
                break

        if success:
            self.state = NodeState.success
            if self.father_node is not None:
                self.apply_theorem()
                self.father_node.check_state()

    def expand(self):
        self.state = NodeState.expanded

        for i in range(len(self.nodes)):
            if self.state == NodeState.success:
                break
            print("\033[34m(pid={},depth={},branch={}/{},nodes={}/{})\033[0m Expanding Node ({}, {})".format(
                self.problem.problem_CDL["id"], self.pos[0], self.pos[1], SuperNode.snc[self.pos[0]],
                i + 1, len(self.nodes), self.nodes[i].predicate, self.nodes[i].item))
            self.nodes[i].expand()

    def apply_theorem(self):
        if self.theorem is None or self.theorem[0].endswith("definition"):
            return

        t_name, t_branch, t_para = self.theorem
        theorem = InverseParserM2F.inverse_parse_logic(  # theorem + para
            t_name, t_para, self.finder.theorem_GDL[t_name]["para_len"])

        letters = {}  # used for vars-letters replacement
        for i in range(len(self.finder.theorem_GDL[t_name]["vars"])):
            letters[self.finder.theorem_GDL[t_name]["vars"][i]] = t_para[i]

        gpl = self.finder.theorem_GDL[t_name]["body"][t_branch]
        premises = []
        passed = True

        for predicate, item in gpl["products"] + gpl["logic_constraints"]:
            oppose = False
            if "~" in predicate:
                oppose = True
                predicate = predicate.replace("~", "")
            item = tuple(letters[i] for i in item)
            has_item = self.problem.condition.has(predicate, item)
            if has_item:
                premises.append(self.problem.condition.get_id_by_predicate_and_item(predicate, item))

            if (not oppose and not has_item) or (oppose and has_item):
                passed = False
                break

        if not passed:
            self.problem.step(theorem, 0)
            return

        for equal, item in gpl["algebra_constraints"]:
            oppose = False
            if "~" in equal:
                oppose = True
            eq = CDLParser.get_equation_from_tree(self.problem, item, True, letters)
            solved_eq = False

            result, premise = EqKiller.solve_target(eq, self.problem)
            if result is not None and rough_equal(result, 0):
                solved_eq = True
            premises += premise

            if (not oppose and not solved_eq) or (oppose and solved_eq):
                passed = False
                break

        if not passed:
            self.problem.step(theorem, 0)
            return

        for predicate, item in gpl["conclusions"]:
            if predicate == "Equal":  # algebra conclusion
                eq = CDLParser.get_equation_from_tree(self.problem, item, True, letters)
                self.problem.add("Equation", eq, premises, theorem)
            else:  # logic conclusion
                item = tuple(letters[i] for i in item)
                self.problem.add(predicate, item, premises, theorem)

        EqKiller.solve_equations(self.problem)
        self.problem.step(theorem, 0)


class BackwardSearcher:

    def __init__(self, predicate_GDL, theorem_GDL, max_depth, strategy):
        """
        Initialize Backward Searcher.
        :param predicate_GDL: predicate GDL.
        :param theorem_GDL: theorem GDL.
        :param max_depth: max search depth.
        :param strategy: <str>, 'df' or 'bf', use deep-first or breadth-first.
        """
        self.predicate_GDL = GDLParser.parse_predicate(predicate_GDL)
        self.theorem_GDL = GDLParser.parse_theorem(theorem_GDL, self.predicate_GDL)
        self.max_depth = max_depth
        self.strategy = strategy
        self.node_map = {}
        self.finder = GoalFinder(self.theorem_GDL, Theorem.t_msg)

        self.problem = None
        self.root = None

        self.id = 0

    def init_problem(self, problem_CDL):
        """Init and return a problem by problem_CDL."""
        s_start_time = time.time()
        self.problem = Problem()
        self.problem.load_problem_by_fl(self.predicate_GDL, CDLParser.parse_problem(problem_CDL))  # load problem
        EqKiller.solve_equations(self.problem)
        self.problem.step("init_problem", time.time() - s_start_time)  # save applied theorem and update step
        SuperNode.snc = {}

    @func_set_timeout(300)
    def search(self):
        """return seqs, <list> of theorem, solved theorem sequences."""
        pid = self.problem.problem_CDL["id"]
        print("\033[36m(pid={})\033[0m Start Searching".format(pid))

        self.root = SuperNode(None, self.problem, None, 1, self.node_map, self.finder)
        if self.problem.goal.type == "algebra":
            eq = self.problem.goal.item - self.problem.goal.answer
            self.root.add_nodes([("Equation", eq)])
        else:
            self.root.add_nodes([(self.problem.goal.item, self.problem.goal.answer)])

        while self.root.state not in [NodeState.success, NodeState.fail]:
            super_node = self.get_super_node()
            if super_node is None:
                break
            start_step_count = self.problem.condition.step_count

            timing = time.time()
            print("\033[35m(pid={},depth={},branch={}/{})\033[0m Expanding SuperNode Start".format(
                pid, super_node.pos[0], super_node.pos[1], SuperNode.snc[super_node.pos[0]]))
            super_node.expand()

            print("\033[35m(pid={},depth={},branch={}/{})\033[0m Expanding SuperNode Done (timing={:.4f})".format(
                pid, super_node.pos[0], super_node.pos[1], SuperNode.snc[super_node.pos[0]], time.time() - timing))

            timing = time.time()
            print("\033[35m(pid={},depth={},branch={}/{})\033[0m Checking Node Start".format(
                pid, super_node.pos[0], super_node.pos[1], SuperNode.snc[super_node.pos[0]]))
            self.check_node(start_step_count)
            print("\033[35m(pid={},depth={},branch={}/{})\033[0m Checking Node End (timing={:.4f})".format(
                pid, super_node.pos[0], super_node.pos[1], SuperNode.snc[super_node.pos[0]],
                time.time() - timing))

        self.problem.check_goal()
        # self.save_backward_tree()

        if self.problem.goal.solved:
            print("\033[32m(pid={})\033[0m End Searching".format(self.problem.problem_CDL["id"]))
            _, seqs = get_used(self.problem)
            return True, seqs

        print("\033[31m(pid={})\033[0m End Searching".format(self.problem.problem_CDL["id"]))
        return False, None

    def get_super_node(self):
        search_stack = deque()
        search_stack.append(self.root)

        while len(search_stack) > 0:
            if self.strategy == "df":
                super_node = search_stack.pop()
            else:
                super_node = search_stack.popleft()

            if super_node.pos[0] > self.max_depth:
                continue

            if super_node.state == NodeState.to_be_expanded:
                return super_node
            elif super_node.state == NodeState.expanded:
                for node in super_node.nodes:
                    if node.state != NodeState.expanded:
                        continue
                    for child_super_node in node.children[::-1]:
                        search_stack.append(child_super_node)

        return None

    def check_node(self, start_step_count):
        end_step_count = self.problem.condition.step_count
        if start_step_count == end_step_count:
            return

        related_pres = []  # new added predicates
        related_eqs = []  # new added/updated equations
        for step in range(start_step_count, end_step_count):
            for _id in self.problem.condition.ids_of_step[step]:
                if self.problem.condition.items[_id][0] == "Equation":
                    if self.problem.condition.items[_id][1] in related_eqs:
                        continue
                    related_eqs.append(self.problem.condition.items[_id][1])
                    for simp_eq in self.problem.condition.simplified_equation:
                        if simp_eq in related_eqs:
                            continue
                        if _id not in self.problem.condition.simplified_equation[simp_eq]:
                            continue
                        related_eqs.append(simp_eq)
                else:
                    predicate, item = self.problem.condition.items[_id][0:2]
                    if (predicate, item) not in self.node_map or (predicate, item) in related_pres:
                        continue
                    related_pres.append((predicate, item))
        for sym in EqKiller.get_minimum_syms(related_eqs, list(self.problem.condition.simplified_equation)):
            if sym not in self.node_map:
                continue
            related_pres.append(sym)

        for related in related_pres:
            for node in self.node_map[related]:
                if node.state in [NodeState.fail, NodeState.success]:
                    continue
                node.expand()

        self.check_node(end_step_count)

    def save_backward_tree(self):
        search_stack = deque()
        search_stack.append((self.root, None))
        dot = Digraph(name=str(self.problem.problem_CDL["id"]))

        while len(search_stack) > 0:
            super_node, father_node_id = search_stack.popleft()
            supernode_id, nodes_id = self.add_supernode(dot, super_node)
            if father_node_id is not None:
                dot.edge(str(father_node_id), str(supernode_id))

            for i in range(len(super_node.nodes)):
                node = super_node.nodes[i]
                node_id = nodes_id[i]
                for child_super_node in node.children:
                    search_stack.append((child_super_node, node_id))

        dot.render(directory="data/solved/bw_tree/", view=False, format="png")

    def add_supernode(self, dot, supernode):
        supernode_id = self.id
        self.id += 1
        nodes_id = []

        if supernode.state == NodeState.to_be_expanded:
            node_text = "state = to_be_expanded"
            fillcolor = "grey"
        elif supernode.state == NodeState.expanded:
            node_text = "state = expanded"
            fillcolor = "blue"
        elif supernode.state == NodeState.success:
            node_text = "state = success"
            fillcolor = "green"
        else:
            node_text = "state = fail"
            fillcolor = "red"
        if supernode.theorem is not None:
            node_text += "\nt_name = {}\nt_branch = {}\nt_para = {}".format(
                supernode.theorem[0], supernode.theorem[1], supernode.theorem[2])
        else:
            node_text += "\nRoot SuperNode"

        dot.node(name=str(supernode_id), label=node_text, shape='box', style='filled', fillcolor=fillcolor)

        for node in supernode.nodes:
            node_text = "predicate = {}\nitem = {}".format(node.predicate, str(node.item))
            if node.state == NodeState.to_be_expanded:
                fillcolor = "grey"
            elif node.state == NodeState.expanded:
                fillcolor = "blue"
            elif node.state == NodeState.success:
                fillcolor = "green"
            else:
                fillcolor = "red"
            dot.node(str(self.id), label=node_text, style='filled', fillcolor=fillcolor)
            dot.edge(str(supernode_id), str(self.id))
            nodes_id.append(self.id)
            self.id += 1

        return supernode_id, nodes_id
