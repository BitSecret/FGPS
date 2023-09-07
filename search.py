from solver.method.interactive import Interactor
from solver.method.forward_search import ForwardSearcher
from solver.method.backward_search import BackwardSearcher
from solver.aux_tools.utils import *
from solver.aux_tools.output import *
from solver.aux_tools.parser import CDLParser
from solver.core.engine import EquationKiller as EqKiller
from func_timeout import FunctionTimedOut
import warnings
import os
import argparse
from colorama import init

init(autoreset=True)
path_gdl = "datasets/gdl/"
path_problems = "datasets/problems/"
path_solved = "datasets/solved/"


def get_args():
    parser = argparse.ArgumentParser(description="Welcome to use FormalGeo!")

    parser.add_argument("--start_pid", type=int, required=True, help="start problem id")
    parser.add_argument("--end_pid", type=int, required=True, help="end problem id")
    parser.add_argument("--direction", type=str, required=True, help="search direction")

    return parser.parse_args()


def main(direction="fw", strategy="df", auto=False, save_seqs=True,
         start_pid=1, end_pid=6981):
    """
    Solve problem by searching.
    :param direction: 'fw' or 'bw', forward search or backward search.
    :param strategy: 'df' or 'bf', deep-first search or breadth-first search.
    :param auto: run all problems or run one problem.
    :param save_seqs: save solved theorem seqs or not.
    :param start_pid: start problem id.
    :param end_pid: end problem id.
    """
    warnings.filterwarnings("ignore")
    if direction == "fw":  # forward search
        searcher = ForwardSearcher(load_json(path_gdl + "predicate_GDL.json"),  # init searcher
                                   load_json(path_gdl + "theorem_GDL.json"),
                                   max_depth=5,
                                   strategy=strategy)
        if auto:
            for filename in os.listdir(path_problems):
                pid = int(filename.split(".")[0])
                if pid < start_pid or pid > end_pid:
                    continue

                problem_CDL = load_json(path_problems + filename)
                if "notes" in problem_CDL or "forward_search" in problem_CDL:
                    continue

                problem = searcher.get_problem(load_json(path_problems + filename))

                try:
                    solved, seqs = searcher.search(problem)
                except FunctionTimedOut:
                    print("\nFunctionTimedOut when search problem {}.\n".format(pid))
                except Exception as e:
                    print("Exception {} when search problem {}.".format(e, pid))
                else:
                    print("pid: {}  solved: {}  seqs:{}\n".format(pid, solved, seqs))
                    if solved and save_seqs:
                        problem_CDL = load_json(path_problems + filename)
                        problem_CDL["forward_search"] = seqs
                        save_json(problem_CDL, path_problems + filename)

        else:
            while True:
                pid = input("pid:")
                filename = "{}.json".format(pid)
                if filename not in os.listdir(path_problems):
                    print("No file \'{}\' in \'{}\'.\n".format(filename, path_problems))
                    continue

                problem = searcher.get_problem(load_json(path_problems + filename))
                solved, seqs = searcher.search(problem, strategy)
                print("pid: {}  solved: {}  seqs:{}\n".format(pid, solved, seqs))
                if solved and save_seqs:  # clean theorem
                    problem_CDL = load_json(path_problems + filename)
                    if "forward_search" not in problem_CDL:
                        problem_CDL["forward_search"] = seqs
                        save_json(problem_CDL, path_problems + filename)
    else:  # backward search
        searcher = BackwardSearcher(load_json(path_gdl + "predicate_GDL.json"),  # init searcher
                                    load_json(path_gdl + "theorem_GDL.json"),
                                    max_depth=15,
                                    strategy=strategy)
        if auto:
            for filename in os.listdir(path_problems):
                pid = int(filename.split(".")[0])
                if pid < start_pid or pid > end_pid:
                    continue

                problem_CDL = load_json(path_problems + filename)
                if "notes" in problem_CDL or "backward_search" in problem_CDL:
                    continue

                searcher.init_problem(load_json(path_problems + filename))

                try:
                    solved, seqs = searcher.search()
                except FunctionTimedOut:
                    print("\nFunctionTimedOut when search problem {}.\n".format(pid))
                except Exception as e:
                    print("Exception {} when search problem {}.".format(e, pid))
                else:
                    print("pid: {}  solved: {}  seqs:{}\n".format(pid, solved, seqs))
                    if solved and save_seqs:
                        problem_CDL = load_json(path_problems + filename)
                        problem_CDL["backward_search"] = seqs
                        save_json(problem_CDL, path_problems + filename)
        else:
            while True:
                pid = input("pid:")
                filename = "{}.json".format(pid)
                if filename not in os.listdir(path_problems):
                    print("No file \'{}\' in \'{}\'.\n".format(filename, path_problems))
                    continue
                searcher.init_problem(load_json(path_problems + filename))
                solved, seqs = searcher.search()

                print("pid: {}  solved: {}  seqs:{}\n".format(pid, solved, seqs))

                if solved and save_seqs:  # clean theorem
                    problem_CDL = load_json(path_problems + filename)
                    if "backward_search" not in problem_CDL:
                        problem_CDL["backward_search"] = seqs
                        save_json(problem_CDL, path_problems + filename)


if __name__ == '__main__':
    main()
