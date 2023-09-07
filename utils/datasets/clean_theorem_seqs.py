import copy
from utils.utils import safe_save_json
from solver.method.interactive import Interactor
from solver.aux_tools.utils import load_json, save_json
from solver.aux_tools.output import get_used
from solver.aux_tools.parser import CDLParser
from solver.core.engine import EquationKiller
import warnings
import time
path_gdl = "../../datasets/gdl/"
path_problems = "../../datasets/problems/"
path_search = "../../datasets/search/"


def main(auto=False, check_search=None, start_pid=1, end_pid=6981):
    solver = Interactor(load_json(path_gdl + "predicate_GDL.json"), load_json(path_gdl + "theorem_GDL.json"))
    search_data = {} if check_search is None else load_json(path_search + "{}.json".format(check_search))

    if auto:
        warnings.filterwarnings("ignore")
        error_problem = []    # (pid, timing, error), problems that raise Exception

        for pid in range(start_pid, end_pid + 1):
            timing = time.time()
            filename = "{}.json".format(pid)
            try:
                problem_CDL = load_json(path_problems + filename)   # get problem msg
                solver.load_problem(problem_CDL)
                if check_search is None:
                    theorem_seqs = problem_CDL["theorem_seqs"]
                else:
                    theorem_seqs = search_data[str(pid)]

                EquationKiller.accurate_mode = True
                for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(theorem_seqs):  # apply theorem seqs
                    solver.apply_theorem(t_name, t_branch, t_para)
                solver.problem.check_goal()
                if not solver.problem.goal.solved:
                    error_problem.append((pid, time.time() - timing, "Can't solve problem using given theorem seqs."))
                    continue

                _, theorem_seqs = get_used(solver.problem)   # forward clean theorem seqs

                EquationKiller.accurate_mode = False
                for i in range(len(theorem_seqs))[::-1]:    # backward clean theorem seqs
                    try_seqs = copy.copy(theorem_seqs)
                    try_seqs.pop(i)
                    solver.load_problem(problem_CDL)
                    for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(try_seqs):
                        solver.apply_theorem(t_name, t_branch, t_para)
                    solver.problem.check_goal()  # check goal after applied theorem seqs
                    if solver.problem.goal.solved:
                        theorem_seqs.pop(i)

                if check_search is None:
                    problem_CDL["theorem_seqs"] = theorem_seqs
                    save_json(problem_CDL, path_problems + filename)
                else:
                    search_data[str(pid)] = theorem_seqs
                print("<CleanTheorem> Problem {} done with timing {}s.".format(pid, time.time() - timing))

            except Exception as e:
                error_problem.append((pid, time.time() - timing, repr(e)))
                continue

        if check_search is not None:
            safe_save_json(search_data, path_search, check_search)

        print("\n<CleanTheorem> Error:")
        for pid, timing, e_msg in error_problem:
            print("{}\t{}\t{}".format(pid, timing, e_msg))

    else:
        while True:
            pid = input("pid:")
            filename = "{}.json".format(pid)
            timing = time.time()
            try:
                problem_CDL = load_json(path_problems + filename)
            except FileNotFoundError as e:
                print(repr(e) + "\n")
                continue

            solver.load_problem(problem_CDL)

            if check_search is None:
                theorem_seqs = problem_CDL["theorem_seqs"]
            else:
                theorem_seqs = search_data[str(pid)]

            EquationKiller.accurate_mode = True
            for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(theorem_seqs):  # apply theorem seqs
                solver.apply_theorem(t_name, t_branch, t_para)
            solver.problem.check_goal()
            if not solver.problem.goal.solved:
                print("<CleanTheorem> Can't solve problem using given theorem seqs.\n")
                continue

            _, theorem_seqs = get_used(solver.problem)  # forward clean theorem seqs

            EquationKiller.accurate_mode = False
            for i in range(len(theorem_seqs))[::-1]:  # backward clean theorem seqs
                try_seqs = copy.copy(theorem_seqs)
                try_seqs.pop(i)
                solver.load_problem(problem_CDL)
                for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(try_seqs):
                    solver.apply_theorem(t_name, t_branch, t_para)
                solver.problem.check_goal()  # check goal after applied theorem seqs
                if solver.problem.goal.solved:
                    theorem_seqs.pop(i)

            if check_search is None:
                problem_CDL["theorem_seqs"] = theorem_seqs
                save_json(problem_CDL, path_problems + filename)
            else:
                search_data[str(pid)] = theorem_seqs
                safe_save_json(search_data, path_search, check_search)
            print("<CleanTheorem> Problem {} done with timing {}s.\n".format(pid, time.time() - timing))


if __name__ == '__main__':
    main(auto=False)
