from FGPSolver.solver.solver import Interactor
from FGPSolver.solver.fw_search import ForwardSearcher
from FGPSolver.solver.bw_search import BackwardSearcher
from FGPSolver.aux_tools.utils import *
from FGPSolver.aux_tools.output import *
from FGPSolver.aux_tools.parser import FormalLanguageParser as FLParser
from FGPSolver.core.engine import EquationKiller as EqKiller
from func_timeout import FunctionTimedOut
import warnings
import os
import argparse
from colorama import init

init(autoreset=True)
path_preset = "data/preset/"
path_formalized = "data/formalized-problems/"
path_solved = "data/solved/"
path_solved_problems = "data/solved/problems/"


def get_args():
    parser = argparse.ArgumentParser(description="Welcome to use FormalGeo!")

    parser.add_argument("--start_pid", type=int, required=True, help="start problem id")
    parser.add_argument("--end_pid", type=int, required=True, help="end problem id")
    parser.add_argument("--direction", type=str, required=True, help="search direction")

    return parser.parse_args()


def save_gdl():
    solver = Interactor(load_json(path_preset + "predicate_GDL.json"),  # init solver
                        load_json(path_preset + "theorem_GDL.json"))
    save_json(solver.predicate_GDL, path_solved + "predicate_parsed.json")
    save_json(solver.theorem_GDL, path_solved + "theorem_parsed.json")
    exit(0)


def check(auto=False, save_CDL=False, clean_theorem=False, acc_mode=False, check_search=None,
          start_pid=1584, end_pid=9831):
    """Run solver and load problem from problem_GDL."""
    solver = Interactor(load_json(path_preset + "predicate_GDL.json"),  # init solver
                        load_json(path_preset + "theorem_GDL.json"))
    EqKiller.accurate_mode = acc_mode

    if auto:  # auto run all problems in formalized-problems
        warnings.filterwarnings("ignore")
        unsolved = []
        print("pid\tannotation\tcorrect_answer\tsolved\tsolved_answer\tspend(s)")
        for filename in os.listdir(path_formalized):
            pid = int(filename.split(".")[0])
            if pid < start_pid or pid > end_pid:
                continue

            problem_CDL = load_json(path_formalized + filename)

            if "notes" in problem_CDL:  # problems can't solve
                if check_search is None:
                    unsolved.append("{}\t{}\t{}".format(
                        problem_CDL["problem_id"], problem_CDL["annotation"], problem_CDL["notes"]))
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

                for theorem_name, theorem_para in FLParser.parse_theorem_seqs(theorem_seqs):
                    solver.apply_theorem(theorem_name, theorem_para)

                solver.problem.check_goal()  # check goal after applied theorem seqs

                if clean_theorem and solver.problem.goal.solved:  # clean theorem
                    problem_CDL = load_json(path_formalized + filename)
                    _id, seqs = get_used_theorem(solver.problem)
                    if check_search is None:
                        problem_CDL["theorem_seqs"] = seqs
                    elif check_search == "fw":
                        problem_CDL["forward_search"] = seqs
                    elif check_search == "bw":
                        problem_CDL["backward_search"] = seqs
                    save_json(problem_CDL, path_formalized + filename)

                simple_show(solver.problem)  # show solved msg

                if save_CDL:  # save solved msg
                    save_json(
                        solver.problem.problem_CDL,
                        path_solved_problems + "{}_parsed.json".format(problem_CDL["problem_id"])
                    )
                    save_step_msg(
                        solver.problem,
                        path_solved_problems
                    )
                    save_solution_tree(
                        solver.problem,
                        path_solved_problems
                    )

            except Exception as e:  # exception
                msg = "Raise Exception <{}> in problem {}.".format(e, filename.split(".")[0])
                unsolved.append("{}\t{}\t{}".format(problem_CDL["problem_id"], problem_CDL["annotation"], msg))

        print("\npid\tannotation\tnotes")
        for n in unsolved:  # show unsolved
            print(n)

    else:  # interactive mode, run one problem according input pid
        while True:
            pid = input("pid:")
            filename = "{}.json".format(pid)
            if filename not in os.listdir(path_formalized):
                print("No file \'{}\' in \'{}\'.\n".format(filename, path_formalized))
                continue

            problem_CDL = load_json(path_formalized + filename)
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

            for theorem_name, theorem_para in FLParser.parse_theorem_seqs(theorem_seqs):
                solver.apply_theorem(theorem_name, theorem_para)

            solver.problem.check_goal()  # check goal after applied theorem seqs

            if clean_theorem and solver.problem.goal.solved:  # clean theorem
                problem_CDL = load_json(path_formalized + filename)
                _id, seqs = get_used_theorem(solver.problem)
                if check_search is None:
                    problem_CDL["theorem_seqs"] = seqs
                elif check_search == "fw":
                    problem_CDL["forward_search"] = seqs
                elif check_search == "bw":
                    problem_CDL["backward_search"] = seqs
                save_json(problem_CDL, path_formalized + filename)

            show(solver.problem)  # show solving process

            if save_CDL:  # save solved msg
                save_json(
                    solver.problem.problem_CDL,
                    path_solved_problems + "{}_parsed.json".format(pid)
                )
                save_step_msg(
                    solver.problem,
                    path_solved_problems
                )
                save_solution_tree(
                    solver.problem,
                    path_solved_problems
                )


def search(direction="fw", strategy="df", auto=False, save_seqs=True,
           start_pid=1584, end_pid=9831):
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
    if direction == "fw":    # forward search
        searcher = ForwardSearcher(load_json(path_preset + "predicate_GDL.json"),  # init searcher
                                   load_json(path_preset + "theorem_GDL.json"),
                                   max_depth=5,
                                   strategy=strategy)
        if auto:
            for filename in os.listdir(path_formalized):
                pid = int(filename.split(".")[0])
                if pid < start_pid or pid > end_pid:
                    continue

                problem_CDL = load_json(path_formalized + filename)
                if "notes" in problem_CDL or "forward_search" in problem_CDL:
                    continue

                problem = searcher.get_problem(load_json(path_formalized + filename))

                try:
                    solved, seqs = searcher.search(problem)
                except FunctionTimedOut:
                    print("\nFunctionTimedOut when search problem {}.\n".format(pid))
                except Exception as e:
                    print("Exception {} when search problem {}.".format(e, pid))
                else:
                    print("pid: {}  solved: {}  seqs:{}\n".format(pid, solved, seqs))
                    if solved and save_seqs:
                        problem_CDL = load_json(path_formalized + filename)
                        problem_CDL["forward_search"] = seqs
                        save_json(problem_CDL, path_formalized + filename)

        else:
            while True:
                pid = input("pid:")
                filename = "{}.json".format(pid)
                if filename not in os.listdir(path_formalized):
                    print("No file \'{}\' in \'{}\'.\n".format(filename, path_formalized))
                    continue

                problem = searcher.get_problem(load_json(path_formalized + filename))
                solved, seqs = searcher.search(problem, strategy)
                print("pid: {}  solved: {}  seqs:{}\n".format(pid, solved, seqs))
                if solved and save_seqs:  # clean theorem
                    problem_CDL = load_json(path_formalized + filename)
                    if "forward_search" not in problem_CDL:
                        problem_CDL["forward_search"] = seqs
                        save_json(problem_CDL, path_formalized + filename)
    else:    # backward search
        searcher = BackwardSearcher(load_json(path_preset + "predicate_GDL.json"),  # init searcher
                                    load_json(path_preset + "theorem_GDL.json"),
                                    max_depth=15,
                                    strategy=strategy)
        if auto:
            for filename in os.listdir(path_formalized):
                pid = int(filename.split(".")[0])
                if pid < start_pid or pid > end_pid:
                    continue

                problem_CDL = load_json(path_formalized + filename)
                if "notes" in problem_CDL or "backward_search" in problem_CDL:
                    continue

                searcher.init_problem(load_json(path_formalized + filename))

                try:
                    solved, seqs = searcher.search()
                except FunctionTimedOut:
                    print("\nFunctionTimedOut when search problem {}.\n".format(pid))
                except Exception as e:
                    print("Exception {} when search problem {}.".format(e, pid))
                else:
                    print("pid: {}  solved: {}  seqs:{}\n".format(pid, solved, seqs))
                    if solved and save_seqs:
                        problem_CDL = load_json(path_formalized + filename)
                        problem_CDL["backward_search"] = seqs
                        save_json(problem_CDL, path_formalized + filename)
        else:
            while True:
                pid = input("pid:")
                filename = "{}.json".format(pid)
                if filename not in os.listdir(path_formalized):
                    print("No file \'{}\' in \'{}\'.\n".format(filename, path_formalized))
                    continue
                searcher.init_problem(load_json(path_formalized + filename))
                solved, seqs = searcher.search()

                print("pid: {}  solved: {}  seqs:{}\n".format(pid, solved, seqs))

                if solved and save_seqs:  # clean theorem
                    problem_CDL = load_json(path_formalized + filename)
                    if "backward_search" not in problem_CDL:
                        problem_CDL["backward_search"] = seqs
                        save_json(problem_CDL, path_formalized + filename)


if __name__ == '__main__':
    check(auto=True, clean_theorem=True, acc_mode=True)
    # save_gdl()

    # search(auto=False, save_seqs=True, direction="bw")

    # args = get_args()
    # search(auto=True, start_pid=args.start_pid, end_pid=args.end_pid, direction=args.direction)
