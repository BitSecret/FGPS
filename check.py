from solver.method.interactive import Interactor
from solver.aux_tools.utils import load_json
from solver.aux_tools.output import show
from solver.aux_tools.parser import CDLParser
import warnings
import time
path_gdl = "datasets/gdl/"
path_problems = "datasets/problems/"
path_search = "datasets/search/"


def simple_show(pid, correct_answer, solved, solved_answer, timing):
    """Show simple information about problem-solving."""
    printed = "{}\t{}\t".format(pid, str(correct_answer))
    if solved:
        printed += "\033[32m1\033[0m\t"
    else:
        printed += "\033[31m0\033[0m\t"
    printed += "{}\t".format(str(solved_answer))
    if timing < 2:
        printed += "{:.6f}".format(timing)
    else:
        printed += "\033[31m{:.6f}\033[0m".format(timing)
    print(printed)


def main(auto=False, check_search=None, start_pid=1, end_pid=6981):
    """Run method and load problem from problem_GDL."""
    solver = Interactor(load_json(path_gdl + "predicate_GDL.json"),  # init method
                        load_json(path_gdl + "theorem_GDL.json"))
    search_data = {} if check_search is None else load_json(path_search + "{}.json".format(check_search))

    if auto:
        warnings.filterwarnings("ignore")
        error_problems = []
        print("pid\tcorrect_answer\tsolved\tsolved_answer\ttiming(s)")

        for pid in range(start_pid, end_pid + 1):
            timing = time.time()
            filename = "{}.json".format(pid)

            try:  # try solve
                problem_CDL = load_json(path_problems + filename)
                solver.load_problem(problem_CDL)
                if check_search is None:
                    theorem_seqs = problem_CDL["theorem_seqs"]
                else:
                    theorem_seqs = search_data[str(pid)]

                for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(theorem_seqs):
                    solver.apply_theorem(t_name, t_branch, t_para)

                solver.problem.check_goal()  # check goal after applied theorem seqs

                simple_show(pid, solver.problem.goal.answer, solver.problem.goal.solved,
                            solver.problem.goal.solved_answer, time.time() - timing)  # show solved msg

            except Exception as e:  # exception
                error_problems.append((pid, repr(e)))

        print("\npid\te_msg")
        for pid, e_msg in error_problems:  # show unsolved
            print("{}\t{}".format(pid, e_msg))

    else:  # interactive mode, run one problem according input pid
        while True:
            pid = input("pid:")
            filename = "{}.json".format(pid)
            try:
                problem_CDL = load_json(path_problems + filename)
                solver.load_problem(problem_CDL)
            except FileNotFoundError as e:
                print(repr(e) + "\n")
                continue

            solver.load_problem(problem_CDL)

            if check_search is None:
                theorem_seqs = problem_CDL["theorem_seqs"]
            else:
                theorem_seqs = search_data[str(pid)]

            for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(theorem_seqs):
                solver.apply_theorem(t_name, t_branch, t_para)

            solver.problem.check_goal()  # check goal after applied theorem seqs

            show(solver.problem)  # show solving process


if __name__ == '__main__':
    main(auto=False)
