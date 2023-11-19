from formalgeo.data import DatasetLoader
from formalgeo.tools import simple_show, load_json, show_solution
from formalgeo.parse import parse_theorem_seqs
from formalgeo.solver import Interactor
import argparse
import warnings
import time


def check_problems(datasets_path, dataset, auto):
    dl = DatasetLoader(dataset, datasets_path)
    solver = Interactor(dl.predicate_GDL, dl.theorem_GDL)
    if auto == "True":
        warnings.filterwarnings("ignore")
        print("pid\tcorrect_answer\tsolved\tsolved_answer\ttiming(s)")

        for pid in range(1, dl.info["problem_number"] + 1):
            timing = time.time()

            try:  # try solve
                problem_CDL = dl.get_problem(pid)
                solver.load_problem(problem_CDL)

                for t_name, t_branch, t_para in parse_theorem_seqs(problem_CDL["theorem_seqs"]):
                    solver.apply_theorem(t_name, t_branch, t_para)

                solver.problem.check_goal()  # check goal after applied theorem seqs

                simple_show(solver.problem, time.time() - timing)  # show solved msg

            except Exception as e:  # exception
                print("Exception: {}".format(repr(e)))

    else:
        while True:
            try:
                pid = input("<pid>:")
                problem_CDL = dl.get_problem(int(pid))
            except BaseException as e:
                print(repr(e) + "\n")
                continue

            solver.load_problem(problem_CDL)

            for t_name, t_branch, t_para in parse_theorem_seqs(problem_CDL["theorem_seqs"]):
                solver.apply_theorem(t_name, t_branch, t_para)

            solver.problem.check_goal()  # check goal after applied theorem seqs

            show_solution(solver.problem)  # show solving process
            print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Welcome to use FGPS!")
    parser.add_argument("--datasets_path", type=str, required=True, help="datasets path")
    parser.add_argument("--dataset", type=str, required=True, help="dataset name")
    parser.add_argument("--auto", type=str, required=True, help="set auto running")
    args = parser.parse_args()

    check_problems(args.datasets_path, args.dataset, args.auto)
