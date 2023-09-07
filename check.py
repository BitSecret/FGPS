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


def save_gdl():
    solver = Interactor(load_json(path_gdl + "predicate_GDL.json"),  # init method
                        load_json(path_gdl + "theorem_GDL.json"))
    save_json(solver.predicate_GDL, path_gdl + "predicate_parsed.json")
    save_json(solver.theorem_GDL, path_gdl + "theorem_parsed.json")


def check(auto=False, save_CDL=False, clean_theorem=False, acc_mode=False, check_search=None,
          start_pid=1, end_pid=6981):
    """Run method and load problem from problem_GDL."""
    solver = Interactor(load_json(path_gdl + "predicate_GDL.json"),  # init method
                        load_json(path_gdl + "theorem_GDL.json"))
    EqKiller.accurate_mode = acc_mode

    if auto:  # auto run all problems in formalized-problems
        warnings.filterwarnings("ignore")
        unsolved = []
        print("pid\tcorrect_answer\tsolved\tsolved_answer\tspend(s)")

        for pid in range(start_pid, end_pid + 1):
            filename = "{}.json".format(pid)
            try:
                problem_CDL = load_json(path_problems + filename)
            except FileNotFoundError:
                continue

            try:  # try solve
                solver.load_problem(problem_CDL)

                theorem_seqs = []
                if check_search is None:
                    theorem_seqs = problem_CDL["theorem_seqs"]
                elif check_search == "fw":
                    if "forward_search" in problem_CDL:
                        theorem_seqs = problem_CDL["forward_search"]
                    else:
                        continue
                elif check_search == "bw":
                    if "backward_search" in problem_CDL:
                        theorem_seqs = problem_CDL["backward_search"]
                    else:
                        continue

                for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(theorem_seqs):
                    solver.apply_theorem(t_name, t_branch, t_para)

                solver.problem.check_goal()  # check goal after applied theorem seqs

                if clean_theorem and solver.problem.goal.solved:  # clean theorem
                    problem_CDL = load_json(path_problems + filename)
                    _id, seqs = get_used(solver.problem)
                    if check_search is None:
                        problem_CDL["theorem_seqs"] = seqs
                    elif check_search == "fw":
                        problem_CDL["forward_search"] = seqs
                    elif check_search == "bw":
                        problem_CDL["backward_search"] = seqs
                    save_json(problem_CDL, path_problems + filename)

                simple_show(solver.problem)  # show solved msg

                if save_CDL:  # save solved msg
                    save_json(
                        solver.problem.problem_CDL,
                        path_solved + "{}_parsed.json".format(pid)
                    )

                    save_solution_tree(

                    )

            except Exception as e:  # exception
                msg = "Raise Exception <{}> in problem {}.".format(e, pid)
                unsolved.append("{}\t{}".format(pid, msg))

        print("\npid\tannotation\tnotes")
        for n in unsolved:  # show unsolved
            print(n)

    else:  # interactive mode, run one problem according input pid
        while True:
            pid = input("pid:")
            filename = "{}.json".format(pid)
            try:
                problem_CDL = load_json(path_problems + filename)
            except FileNotFoundError:
                print("No file \'{}\' in \'{}\'.\n".format(filename, path_problems))
                continue

            solver.load_problem(problem_CDL)

            theorem_seqs = []
            if check_search is None:
                theorem_seqs = problem_CDL["theorem_seqs"]
            elif check_search == "fw":
                if "forward_search" in problem_CDL:
                    theorem_seqs = problem_CDL["forward_search"]
                else:
                    print("No forward search seqs.")
                    continue
            elif check_search == "bw":
                if "backward_search" in problem_CDL:
                    theorem_seqs = problem_CDL["backward_search"]
                else:
                    print("No backward search seqs.")
                    continue

            for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(theorem_seqs):
                solver.apply_theorem(t_name, t_branch, t_para)

            solver.problem.check_goal()  # check goal after applied theorem seqs

            if clean_theorem and solver.problem.goal.solved:  # clean theorem
                problem_CDL = load_json(path_problems + filename)
                _id, seqs = get_used(solver.problem)
                if check_search is None:
                    problem_CDL["theorem_seqs"] = seqs
                elif check_search == "fw":
                    problem_CDL["forward_search"] = seqs
                elif check_search == "bw":
                    problem_CDL["backward_search"] = seqs
                save_json(problem_CDL, path_problems + filename)

            show(solver.problem)  # show solving process

            if save_CDL:  # save solved msg
                save_json(
                    solver.problem.problem_CDL,
                    path_solved + "{}_parsed.json".format(pid)
                )
                save_step_msg(
                    solver.problem,
                    path_solved
                )
                save_solution_tree(
                    solver.problem,
                    path_solved
                )


def search(direction="fw", strategy="df", auto=False, save_seqs=True,
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
    # save_gdl()
    check(auto=False, save_CDL=False, clean_theorem=False, start_pid=1, end_pid=6981)
    # save_gdl()

    # search(auto=False, save_seqs=True, direction="bw")

    # args = get_args()
    # search(auto=True, start_pid=args.start_pid, end_pid=args.end_pid, direction=args.direction)
