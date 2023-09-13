import time
import random
import warnings
from func_timeout import func_set_timeout
from solver.problem.problem import Problem
from solver.aux_tools.parser import GDLParser, CDLParser
from solver.aux_tools.parser import InverseParserM2F
from solver.core.engine import EquationKiller as EqKiller
from solver.core.engine import GeometryPredicateLogic as GeoLogic
from solver.aux_tools.output import get_used
from solver.aux_tools.utils import load_json
from utils.utils import debug_print

path_gdl = "../../datasets/gdl/"
path_problems = "../../datasets/problems/"
path_search_log = "../../utils/search/"


class Node:

    def __init__(self, base_problem, father, father_selection, pos, theorem_GDL, p2t_map, debug=False):
        """
        Init forward search tree Node.
        :param base_problem: Instance of <solver.problem.Problem>.
        :param father: Father node.
        :param father_selection: ((t_name, t_branch, t_para), ((predicate, item, premise),)).
        :param pos: <tuple>, (depth, width, index).
        :param theorem_GDL: theorem GDL.
        :param p2t_map: msg problem-solving needed.
        :param debug: <bool>, set True when need print process information.
        """
        self.base_problem = base_problem
        self.theorem_GDL = theorem_GDL
        self.p2t_map = p2t_map

        self.father = father
        self.father_selection = father_selection  # apply father_selection then get current node
        self.pos = pos
        self.debug = debug

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
            theorem = InverseParserM2F.inverse_parse_one_theorem(t_name, t_branch, t_para, self.theorem_GDL)

            for predicate, item, premise in conclusions:
                if predicate == "Equation":  # reparse symbolic expr to adapt current problem
                    item = CDLParser.parse_expr(problem, str(item))
                problem.add(predicate, item, premise, theorem, skip_check=True)
            problem.step(theorem, 0)

        if self.father_selection is not None:  # apply current theorem selection
            self.last_step = problem.condition.step_count
            update = False
            t_msg, conclusions = self.father_selection
            t_name, t_branch, t_para = t_msg
            theorem = InverseParserM2F.inverse_parse_one_theorem(t_name, t_branch, t_para, self.theorem_GDL)

            for predicate, item, premise in conclusions:
                if predicate == "Equation":
                    item = CDLParser.parse_expr(problem, str(item))
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

        timing = time.time()
        self.selections = self.get_theorem_selection(problem)
        for i in range(len(self.selections))[::-1]:
            if self.selections[i] in unapplied_selections or self.selections[i] in applied_selections:
                self.selections.pop(i)
        debug_print(self.debug, "(depth={}, width={}, index={}, timing={:.4f}s) Get {} selections.".
                    format(self.pos[0], self.pos[1], self.pos[2], time.time() - timing, len(self.selections)))

        nodes = []
        children_selections = unapplied_selections + self.selections
        for i in range(len(children_selections)):
            pos = (self.pos[0] + 1, len(children_selections), i + 1)
            nodes.append(Node(self.base_problem, self, children_selections[i], pos,
                              self.theorem_GDL, self.p2t_map, self.debug))

        return nodes

    def get_theorem_selection(self, problem):
        """
        Return theorem selections according to <self.last_step>.
        :return selections: <list> of ((t_name, t_branch, t_para), ((predicate, item, premise))).
        """
        selections = []

        problem_p_paras = set()  # Perimeter
        problem_a_paras = set()  # Area
        for sym in problem.condition.attr_of_sym:
            predicate, paras = problem.condition.attr_of_sym[sym]
            if predicate.startswith("Perimeter"):
                for para in paras:
                    problem_p_paras.add(para)
            elif predicate.startswith("Area"):
                for para in paras:
                    problem_a_paras.add(para)

        timing = time.time()
        related_pres = []  # new added predicates
        related_syms = []  # new added/updated equations
        for step in range(self.last_step, problem.condition.step_count):  # get related conditions
            for _id in problem.condition.ids_of_step[step]:
                if problem.condition.items[_id][0] == "Equation":
                    for sym in problem.condition.items[_id][1].free_symbols:
                        if sym in related_syms:
                            continue
                        related_syms.append(sym)
                else:
                    if problem.condition.items[_id][0] not in self.p2t_map:
                        continue
                    item = problem.condition.items[_id][1]
                    for t_name, t_branch, p_vars in self.p2t_map[problem.condition.items[_id][0]]:
                        if len(p_vars) != len(item):
                            continue
                        letters = {}
                        for i in range(len(p_vars)):
                            letters[p_vars[i]] = item[i]
                        related_pre = (t_name, t_branch, letters)
                        if related_pre not in related_pres:
                            related_pres.append(related_pre)
        debug_print(self.debug, "(pos={}, timing={:.4f}s) Get Related.".format(self.pos, time.time() - timing))
        debug_print(self.debug, "(pos={}) Related predicates: {}.".format(self.pos, related_pres))
        debug_print(self.debug, "(pos={}) Related syms: {}.".format(self.pos, related_syms))

        timing = time.time()
        logic_selections = self.try_theorem_logic(problem, related_pres)
        debug_print(self.debug, "(pos={}, timing={:.4f}s) Get {} logic-related selections: {}.".format(
            self.pos, time.time() - timing, len(logic_selections), logic_selections))
        timing = time.time()
        algebra_selections = self.try_theorem_algebra(problem, related_syms)
        debug_print(self.debug, "(pos={}, timing={:.4f}s) Get {} algebra-related selections: {}.".format(
            self.pos, time.time() - timing, len(algebra_selections), algebra_selections))

        timing = time.time()
        added_selections = []
        for selection in logic_selections + algebra_selections:  # remove redundancy
            _, conclusions = selection
            s = []
            for conclusion in conclusions:
                predicate, item, _ = conclusion
                s.append((predicate, item))
            s = tuple(s)
            if s not in added_selections:
                added_selections.append(s)
                selections.append(selection)

        for i in range(len(selections))[::-1]:
            t_msg, conclusions = selections[i]
            t_name, t_branch, t_para = t_msg
            if "area" in t_name:
                if "ratio" in t_name:
                    para1 = t_para[0:int(len(t_para) / 2)]
                    para2 = t_para[int(len(t_para) / 2):]
                    if not (para1 in problem_a_paras and para2 in problem_a_paras):
                        selections.pop(i)
                else:
                    if t_para not in problem_a_paras:
                        selections.pop(i)
            elif "perimeter" in t_name:
                if "ratio" in t_name:
                    para1 = t_para[0:int(len(t_para) / 2)]
                    para2 = t_para[int(len(t_para) / 2):]
                    if not (para1 in problem_p_paras and para2 in problem_p_paras):
                        selections.pop(i)
                else:
                    if t_para not in problem_p_paras:
                        selections.pop(i)
        debug_print(self.debug, "(pos={}, timing={:.4f}s) Get {}  selections: {}.".format(
            self.pos, time.time() - timing, len(selections), selections))

        return selections

    def try_theorem_logic(self, problem, related_pres):
        """
        Try a theorem and return can-added conclusions.
        :param problem: <Problem>, rebuild problem.
        :param related_pres: <list>, list of tuple('t_name', 't_branch', letters).
        :return selections: <list> of ((t_name, t_branch, t_para, t_timing), ((predicate, item, premise))).
        """

        selections = []
        for t_name, t_branch, t_letters in related_pres:
            gpl = self.theorem_GDL[t_name]["body"][t_branch]
            results = GeoLogic.run(gpl, problem, t_letters)  # get gpl reasoned result
            for letters, premise, conclusion in results:
                t_para = tuple([letters[i] for i in self.theorem_GDL[t_name]["vars"]])

                premise = tuple(premise)
                conclusions = []
                for predicate, item in conclusion:  # add conclusion
                    if problem.check(predicate, item, premise, t_name):
                        if predicate != "Equation":
                            item = tuple(item)
                        conclusions.append((predicate, item, premise))

                if len(conclusions) > 0:
                    selections.append(((t_name, t_branch, t_para), tuple(conclusions)))

        return selections

    def try_theorem_algebra(self, problem, related_syms):
        """
        Try a theorem and return can-added conclusions.
        :param problem: <Problem>, rebuild problem.
        :param related_syms: <list>, related syms.
        :return selections: <list> of ((t_name, t_branch, t_para, t_timing), ((predicate, item, premise))).
        """
        paras_of_attrs = {}  # <dict>, {attr: [para]}
        for sym in related_syms:
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
            for t_name, t_branch, p_vars in self.p2t_map[related_attr]:
                gpl = self.theorem_GDL[t_name]["body"][t_branch]  # run gdl
                for related_para in related_paras:
                    letters = {}
                    for i in range(len(p_vars)):
                        letters[p_vars[i]] = related_para[i]
                    results = GeoLogic.run(gpl, problem, letters)  # get gpl reasoned result
                    for letters, premise, conclusion in results:
                        theorem_para = tuple([letters[i] for i in self.theorem_GDL[t_name]["vars"]])
                        premise = tuple(premise)
                        conclusions = []
                        for predicate, item in conclusion:  # add conclusion
                            if problem.check(predicate, item, premise, t_name):
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
        :param p2t_map: <dict>, {predicate/attr: [(theorem_name, branch, p_vars)]}, map predicate to theorem.
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

        self.step_size = 0

    def init_search(self, problem_CDL):
        """Initial problem by problem_CDL and build root Node."""
        self.step_size = 0
        EqKiller.use_cache = True    # use cache to speed up solving
        EqKiller.cache_eqs = {}
        EqKiller.cache_target = {}

        timing = time.time()  # timing

        self.problem = Problem()
        self.problem.load_problem_by_fl(self.predicate_GDL, CDLParser.parse_problem(problem_CDL))  # load problem
        EqKiller.solve_equations(self.problem)
        self.problem.step("init_problem", 0)  # save applied theorem and update step

        root = Node(self.problem, None, None, (1, 1, 1), self.theorem_GDL, self.p2t_map, debug=self.debug)
        self.stack = []
        self.stack.append(root)

        debug_print(self.debug, "(pid={}, method={}, timing={:.4f}s) Initialize and start forward search...".format(
            problem_CDL["problem_id"], self.method, time.time() - timing))

    @func_set_timeout(300)
    def search(self):
        """
        Search problem and return search result.
        :return solved: <bool>, indicate whether problem solved or not.
        :return seqs: <list> of <str>, solved theorem sequences.
        """
        if self.method == "bfs":  # breadth-first search
            while len(self.stack) > 0:
                node = self.stack.pop(0)
                self.step_size += 1
                debug_print(self.debug, "\n(depth={}, width={}, index={}) Current node.".format(
                    node.pos[0], node.pos[1], node.pos[2]))
                timing = time.time()
                problem, solved = node.check_goal()
                debug_print(self.debug, "(pos={}, solved={}, timing={:.4f}s) Check goal.".format(
                    node.pos, solved, time.time() - timing))
                if solved is None:  # not update, close search branch
                    continue
                if solved:  # solved, return result
                    _, seqs = get_used(problem)
                    return True, seqs
                else:  # continue search
                    timing = time.time()
                    child_nodes = node.get_children(problem)
                    for child_node in child_nodes:
                        self.stack.append(child_node)
                    debug_print(self.debug, "(pos={}, timing={:.4f}s) Expand {} child node.".
                                format(node.pos, time.time() - timing, len(child_nodes)))
        elif self.method == "dfs":  # deep-first search
            while len(self.stack) > 0:
                node = self.stack.pop()
                self.step_size += 1
                debug_print(self.debug, "\n(depth={}, width={}, index={}) Current node.".format(
                    node.pos[0], node.pos[1], node.pos[2]))
                timing = time.time()
                problem, solved = node.check_goal()
                debug_print(self.debug, "(pos={}, solved={}, timing={:.4f}s) Check goal.".format(
                    node.pos, solved, time.time() - timing))
                if solved is None:  # not update, close search branch
                    continue
                if solved:  # solved, return result
                    _, seqs = get_used(problem)
                    return True, seqs
                else:  # continue search
                    timing = time.time()
                    child_nodes = node.get_children(problem)
                    for child_node in child_nodes:
                        self.stack.append(child_node)
                    debug_print(self.debug, "(pos={}, timing={:.4f}s) Expand {} child node.".
                                format(node.pos, time.time() - timing, len(child_nodes)))
        elif self.method == "rs":  # random search
            while len(self.stack) > 0:
                node = self.stack.pop(random.randint(0, len(self.stack) - 1))
                self.step_size += 1
                debug_print(self.debug, "\n(depth={}, width={}, index={}) Current node.".format(
                    node.pos[0], node.pos[1], node.pos[2]))
                timing = time.time()
                problem, solved = node.check_goal()
                debug_print(self.debug, "(pos={}, solved={}, timing={:.4f}s) Check goal.".format(
                    node.pos, solved, time.time() - timing))
                if solved is None:  # not update, close search branch
                    continue
                if solved:  # solved, return result
                    _, seqs = get_used(problem)
                    return True, seqs
                else:  # continue search
                    timing = time.time()
                    child_nodes = node.get_children(problem)
                    for child_node in child_nodes:
                        self.stack.append(child_node)
                    debug_print(self.debug, "(pos={}, timing={:.4f}s) Expand {} child node.".
                                format(node.pos, time.time() - timing, len(child_nodes)))
        else:  # beam search
            while len(self.stack) > 0:
                if len(self.stack) > self.beam_size:  # select branch with beam size
                    stack = []
                    for i in random.sample(range(len(self.stack)), self.beam_size):
                        stack.append(self.stack[i])
                    self.stack = stack

                new_stack = []
                for node in self.stack:  # expand all selected branch
                    self.step_size += 1
                    debug_print(self.debug, "\n(depth={}, width={}, index={}) Current node.".format(
                        node.pos[0], node.pos[1], node.pos[2]))
                    timing = time.time()
                    problem, solved = node.check_goal()
                    debug_print(self.debug, "(pos={}, solved={}, timing={:.4f}s) Check goal.".format(
                        node.pos, solved, time.time() - timing))
                    if solved is None:  # not update, close search branch
                        continue
                    if solved:  # solved, return result
                        _, seqs = get_used(problem)
                        return True, seqs
                    else:  # continue search
                        timing = time.time()
                        child_nodes = node.get_children(problem)
                        for child_node in child_nodes:
                            new_stack.append(child_node)
                        debug_print(self.debug, "(pos={}, timing={:.4f}s) Expand {} child node.".
                                    format(node.pos, time.time() - timing, len(child_nodes)))

                self.stack = new_stack

        return False, None


if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    searcher = ForwardSearcher(
        load_json(path_gdl + "predicate_GDL.json"), load_json(path_gdl + "theorem_GDL.json"),
        method="bfs", max_depth=5, beam_size=5,
        p2t_map=load_json(path_search_log + "p2t_map-fw.json"), debug=True
    )
    pid = 1
    searcher.init_search(load_json(path_problems + "{}.json".format(pid)))
    result = searcher.search()
    print("pid: {}, solved: {}, seqs:{}, step_count: {}.\n".format(pid, result[0], result[1], searcher.step_size))
