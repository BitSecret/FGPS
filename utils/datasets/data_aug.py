import sys
sys.path.append("../..")
from solver.method.interactive import Interactor
from solver.method.forward_search import Theorem
from solver.aux_tools.utils import *
from solver.aux_tools.output import *
from solver.aux_tools.parser import CDLParser
from solver.aux_tools.parser import InverseParserM2F
from func_timeout import FunctionTimedOut, func_set_timeout
import warnings
import os
path_problems = "../../datasets/problems/"
path_gdl = "../../datasets/gdl/"


class Expander:
    def __init__(self, use_theorem):
        warnings.filterwarnings("ignore")
        self.use_theorem = use_theorem
        self.solver = Interactor(load_json(path_gdl + "predicate_GDL.json"),
                                 load_json(path_gdl + "theorem_GDL.json"))
        if "log.json" not in os.listdir(path_problems):
            self.log = {}
            self.count = len(os.listdir(path_problems)) + 1
        else:
            self.log = load_json(path_problems + "log.json")
            self.count = len(os.listdir(path_problems))
        self.raw_pid = 0
        self.data = []

    def expand(self, start_pid, end_pid):
        for self.raw_pid in range(start_pid, end_pid + 1):
            if end_pid > 6981:
                break
            problem_CDL = load_json(path_problems + "{}.json".format(self.raw_pid))

            print("\033[36m(pid={})\033[0m Start Expanding.".format(self.raw_pid))
            self.init_problem(problem_CDL)  # apply theorem or random search
            self.data = []
            self.expand_logic()
            self.expand_algebra()
            self.save_expand()

    @func_set_timeout(60)
    def apply_all_theorem(self):
        timing = time.time()
        count = 0
        update = True
        while update:
            update = False
            for theorem_name in Theorem.t_msg:
                if Theorem.t_msg[theorem_name][0] != 1:
                    continue
                update = self.solver.apply_theorem(theorem_name) or update
                print("\033[34m(pid={},use_theorem=False,timing={:.4f}s,count={})\033[0m Apply theorem <{}>.".format(
                    self.raw_pid, time.time() - timing, count, theorem_name))
                count += 1

        update = True
        while update:
            update = False
            for theorem_name in Theorem.t_msg:
                if Theorem.t_msg[theorem_name][0] == 3:
                    continue
                update = self.solver.apply_theorem(theorem_name) or update
                print("\033[34m(pid={},use_theorem=False,timing={:.4f}s,count={})\033[0m Apply theorem <{}>.".format(
                    self.raw_pid, time.time() - timing, count, theorem_name))
                count += 1

    def init_problem(self, problem_CDL):
        self.solver.load_problem(problem_CDL)
        if self.use_theorem:
            timing = time.time()
            count = 0
            for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(problem_CDL["theorem_seqs"]):
                self.solver.apply_theorem(t_name, t_branch, t_para)
                print("\033[34m(pid={},use_theorem=True,timing={:.4f}s,count={})\033[0m Apply theorem <{}>".format(
                    self.raw_pid, time.time() - timing, count, t_name))
                count += 1
        else:
            try:
                self.apply_all_theorem()
            except FunctionTimedOut as e:
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
            if "Equation" in goal_GDL:
                goal_GDL = goal_GDL.replace("Equation", "Value")

            if predicate != "Equation":  # logic
                problem_answer = goal_GDL
                goal_GDL = "Relation({})".format(goal_GDL)
            else:  # algebra
                problem_answer = "0"

            for added_conditions, theorem_seqs in self.get_expand_problems(cid):
                self.data.append((added_conditions, goal_GDL, problem_answer, theorem_seqs))

    def expand_algebra(self):
        problem = self.solver.problem
        for sym in problem.condition.value_of_sym:
            value = problem.condition.value_of_sym[sym]
            if value is None:
                continue
            try:
                cid = problem.condition.id_of_item[("Equation", sym - value)]
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
        if str(self.raw_pid) not in self.log:  # ensure no duplicate problems
            self.log[str(self.raw_pid)] = []
        else:
            for pid in self.log[str(self.raw_pid)]:
                problem_cdl = load_json(path_problems + "{}.json".format(pid))
                all_expanded_data.add((tuple(problem_cdl["text_cdl"]), problem_cdl["goal_cdl"]))

        raw_problem_cdl = load_json(path_problems + "{}.json".format(self.raw_pid))

        for added_conditions, goal_GDL, problem_answer, theorem_seqs in self.data:
            text_cdl = raw_problem_cdl["text_cdl"] + added_conditions
            if (tuple(text_cdl), goal_GDL) in all_expanded_data:
                continue
            # print(added_conditions, goal_GDL, problem_answer, theorem_seqs)
            all_expanded_data.add((tuple(text_cdl), goal_GDL))

            new_data = {
                "problem_id": self.count,
                "annotation": "Expander_2023-09-01",
                "source": "FormalGeo-{}".format(self.raw_pid),
                "problem_level": 1,
                "problem_text_cn": "",
                "problem_text_en": "",
                "problem_img": "{}.png".format(self.raw_pid),
                "construction_cdl": raw_problem_cdl["construction_cdl"],
                "text_cdl": text_cdl,
                "image_cdl": raw_problem_cdl["image_cdl"],
                "goal_cdl": goal_GDL,
                "problem_answer": problem_answer,
                "theorem_seqs": theorem_seqs
            }

            save_json(new_data, path_problems + "{}.json".format(self.count))
            self.log[str(self.raw_pid)].append(self.count)
            self.count += 1

        save_json(self.log, path_problems + "log_bk.json")
        try:
            os.remove(path_problems + "log.json")
        except FileNotFoundError:
            pass
        os.rename(path_problems + "log_bk.json", path_problems + "log.json")
        print("\033[34m(pid={},count={})\033[0m Save Expanded.\n".format(self.raw_pid, len(self.data)))


if __name__ == '__main__':
    # expander = Expander(use_theorem=True)
    # expander.expand(start_pid=1, end_pid=6981)
    expander = Expander(use_theorem=False)
    expander.expand(start_pid=1, end_pid=6981)
