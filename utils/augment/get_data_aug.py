from solver.method.interactive import Interactor
from solver.aux_tools.utils import *
from solver.aux_tools.output import *
from solver.aux_tools.parser import CDLParser
from solver.aux_tools.parser import InverseParserM2F
from solver.core.engine import EquationKiller
from utils.utils import safe_save_json
from func_timeout import FunctionTimedOut, func_set_timeout
import warnings
import os
import copy

raw_problem_count = 6981
path_problems = "../../datasets/problems/"
path_problems_augment = "../../datasets/problems-augment/"
path_gdl = "../../datasets/gdl/"
path_search_log = "../search/"


def init_aug_log():
    log = {
        "pid_count": raw_problem_count + 1,  # augmentation pid
        "break_pid": {  # raw pid
            "interactive": 1,
            "search": 1
        }
    }
    save_json(log, "aug_log.json")


class Expander:
    def __init__(self, method):
        """
        :param method: 'interactive' or 'search'.
        """
        warnings.filterwarnings("ignore")
        self.solver = Interactor(load_json(path_gdl + "predicate_GDL.json"),
                                 load_json(path_gdl + "theorem_GDL.json"))
        self.method = method
        if method == "search":
            EquationKiller.use_cache = True

        self.log = load_json("aug_log.json")
        self.t_msg = load_json(path_search_log + "t_msg.json")
        self.data = None

    def expand(self):
        while self.log["break_pid"][self.method] < raw_problem_count + 1:
            problem_CDL = load_json(path_problems + "{}.json".format(self.log["break_pid"][self.method]))

            print("\033[36m(pid={})\033[0m Start Expanding.".format(self.log["break_pid"][self.method]))
            self.init_problem(problem_CDL)  # apply theorem or random search
            self.data = []
            self.expand_logic()
            self.expand_algebra()
            self.save_expand()

    @func_set_timeout(300)
    def apply_all_theorem(self):
        timing = time.time()
        count = 0
        update = True
        while update:
            update = False
            for t_name in self.t_msg:
                if self.t_msg[t_name][0] != 1:
                    continue
                update = self.solver.apply_theorem(t_name) or update
                print("\033[34m(pid={},use_theorem=False,timing={:.4f}s,count={})\033[0m Apply theorem <{}>.".format(
                    self.log["break_pid"][self.method], time.time() - timing, count, t_name))
                count += 1

        update = True
        while update:
            update = False
            for t_name in self.t_msg:
                if self.t_msg[t_name][0] == 3:
                    continue
                update = self.solver.apply_theorem(t_name) or update
                print("\033[34m(pid={},use_theorem=False,timing={:.4f}s,count={})\033[0m Apply theorem <{}>.".format(
                    self.log["break_pid"][self.method], time.time() - timing, count, t_name))
                count += 1

    def init_problem(self, problem_CDL):
        EquationKiller.cache_eqs = {}  # init cache
        EquationKiller.cache_target = {}
        self.solver.load_problem(problem_CDL)
        if self.method == "interactive":
            timing = time.time()
            count = 0
            for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(problem_CDL["theorem_seqs"]):
                self.solver.apply_theorem(t_name, t_branch, t_para)
                print("\033[34m(pid={},use_theorem=True,timing={:.4f}s,count={})\033[0m Apply theorem <{}>".format(
                    self.log["break_pid"][self.method], time.time() - timing, count, t_name))
                count += 1
        else:
            try:
                self.apply_all_theorem()
            except FunctionTimedOut:
                pass

    def expand_logic(self):
        problem = self.solver.problem
        for cid in range(len(problem.condition.items)):
            predicate, item, premise, theorem, step = problem.condition.items[cid]
            if predicate in ["Shape", "Collinear", "Cocircular", "Point", "Line", "Arc",
                             "Angle", "Polygon", "Circle"] \
                    or theorem == "prerequisite":
                continue

            goal_GDL = InverseParserM2F.inverse_parse_one(predicate, item, problem)
            if "Equation" in goal_GDL or "Value" in goal_GDL:
                continue

            if "Equal" in goal_GDL:  # algebra
                problem_answer = "0"
            else:  # logic
                problem_answer = goal_GDL
                goal_GDL = "Relation({})".format(goal_GDL)

            for added_conditions, theorem_seqs in self.get_expand_problems(cid):
                self.data.append((added_conditions, goal_GDL, problem_answer, theorem_seqs))

    def expand_algebra(self):
        problem = self.solver.problem
        for sym in problem.condition.value_of_sym:
            value = problem.condition.value_of_sym[sym]
            if value is None:
                continue
            try:
                cid = problem.condition.get_id_by_predicate_and_item("Equation", sym - value)
            except KeyError:
                continue

            problem_answer = str(value).replace(" ", "")
            attr, paras = problem.condition.attr_of_sym[sym]
            if attr == "Free":
                goal_GDL = "Value(" + "".join(paras[0]) + ")"
            else:
                goal_GDL = "Value(" + attr + "(" + "".join(paras[0]) + "))"

            for added_conditions, theorem_seqs in self.get_expand_problems(cid):
                self.data.append((added_conditions, goal_GDL, problem_answer, theorem_seqs))

    def get_expand_problems(self, cid):
        problem = self.solver.problem
        expanded_problems = []
        theorem_seqs = []
        _, _, premise, theorem, _ = problem.condition.items[cid]

        if theorem not in ["solve_eq", "prerequisite", "extended"]:
            theorem_seqs.append(theorem)
        premises = self.select_premises(list(premise))

        while len(premises) > 0:
            if len(theorem_seqs) > 0:
                added_conditions = []
                for i in premises:
                    predicate, item, _, _, _ = problem.condition.items[i]
                    condition = InverseParserM2F.inverse_parse_one(predicate, item, problem)
                    if "Value" in condition:
                        condition = condition.replace("Value", "Equal")
                    added_conditions.append(condition)
                expanded_problems.append((added_conditions, theorem_seqs[::-1]))

            _, _, premise, theorem, _ = problem.condition.items[premises[0]]
            premises.pop(0)
            premises += list(premise)
            theorem_seqs.append(theorem)
            for i in range(len(premises))[::-1]:
                _, _, new_premise, new_theorem, _ = problem.condition.items[premises[i]]
                if premise == new_premise and theorem == new_theorem:
                    premises.pop(i)
            premises = self.select_premises(premises)

        if len(theorem_seqs) > 0:
            expanded_problems.append(([], theorem_seqs[::-1]))

        return expanded_problems

    def select_premises(self, premises):
        problem = self.solver.problem

        update = True
        while update and len(premises) > 0:
            update = False
            new_premises = set()

            for i in premises:
                _, _, premise, theorem, _ = problem.condition.items[i]
                if theorem not in ["solve_eq", "prerequisite", "extended"]:
                    new_premises.add(i)
                else:
                    for p in premise:
                        if p != -1:
                            new_premises.add(p)
                            update = True

            premises = new_premises

        return list(premises)

    def save_expand(self):
        all_expanded_data = set()
        if "{}.json".format(self.log["break_pid"][self.method]) not in os.listdir(
                path_problems_augment):  # ensure no duplicate problems
            expanded = {}
        else:
            expanded = load_json(path_problems_augment + "{}.json".format(self.log["break_pid"][self.method]))
            for pid in expanded:
                all_expanded_data.add((tuple(expanded[pid]["added_cdl"]), expanded[pid]["goal_cdl"]))

        for added_conditions, goal_GDL, problem_answer, theorem_seqs in self.data:
            if (tuple(added_conditions), goal_GDL) in all_expanded_data:
                continue

            cleaned_theorem_seqs = []
            for theorem in theorem_seqs:
                if theorem not in cleaned_theorem_seqs:
                    cleaned_theorem_seqs.append(theorem)

            new_data = {
                "problem_id": self.log["pid_count"],
                "added_cdl": added_conditions,
                "goal_cdl": goal_GDL,
                "problem_answer": problem_answer,
                "theorem_seqs": cleaned_theorem_seqs
            }
            expanded[str(self.log["pid_count"])] = new_data
            self.log["pid_count"] += 1

        save_json(expanded, path_problems_augment + "{}.json".format(self.log["break_pid"][self.method]))
        self.log["break_pid"][self.method] += 1
        safe_save_json(self.log, "", "aug_log")
        print("\033[34m(pid={},count={})\033[0m Save Expanded.\n".format(
            self.log["break_pid"][self.method] - 1, len(self.data)))


def assemble(raw_problem, aug_problem):
    raw_problem = copy.copy(raw_problem)
    raw_problem["problem_id"] = aug_problem["problem_id"]
    raw_problem["text_cdl"] += aug_problem["added_cdl"]
    raw_problem["goal_cdl"] = aug_problem["goal_cdl"]
    raw_problem["problem_answer"] = aug_problem["problem_answer"]
    raw_problem["theorem_seqs"] = aug_problem["theorem_seqs"]
    return raw_problem


if __name__ == '__main__':
    # init_aug_log()
    expander = Expander(method="interactive")
    expander.expand()
