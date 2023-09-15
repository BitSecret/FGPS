from solver.method.interactive import Interactor
from solver.aux_tools.utils import load_json
from solver.aux_tools.output import show
from solver.aux_tools.parser import CDLParser
from utils.augment.get_data_aug import assemble
import warnings
import time

path_gdl = "datasets/gdl/"
path_problems = "datasets/problems/"
path_problems_augment = "datasets/problems-augment/"
path_search_data = "datasets/solved/search/"


def simple_show(pid, correct_answer, solved, solved_answer, timing, raw_pid=None):
    """Show simple information about problem-solving."""
    if raw_pid is not None:
        printed = "{}\t{}\t{}\t".format(raw_pid, pid, str(correct_answer))
    else:
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


def check_raw(auto=False, start_pid=1, end_pid=6981):
    """Run method and load problem from problem_GDL."""
    solver = Interactor(load_json(path_gdl + "predicate_GDL.json"),  # init method
                        load_json(path_gdl + "theorem_GDL.json"))
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

                for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(problem_CDL["theorem_seqs"]):
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
            try:
                pid = input("pid:")
                filename = "{}.json".format(pid)
                problem_CDL = load_json(path_problems + filename)
            except BaseException as e:
                print(repr(e) + "\n")
                continue

            solver.load_problem(problem_CDL)

            for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(problem_CDL["theorem_seqs"]):
                solver.apply_theorem(t_name, t_branch, t_para)

            solver.problem.check_goal()  # check goal after applied theorem seqs

            show(solver.problem)  # show solving process


def check_augment(auto=False, start_pid=1, end_pid=6981, show_solved=True):
    """Run method and load problem from problem_GDL."""
    solver = Interactor(load_json(path_gdl + "predicate_GDL.json"),  # init method
                        load_json(path_gdl + "theorem_GDL.json"))

    if auto:
        warnings.filterwarnings("ignore")
        error_problems = []
        print("raw_pid\tpid\tcorrect_answer\tsolved\tsolved_answer\ttiming(s)")

        for raw_pid in range(start_pid, end_pid + 1):
            try:
                filename = "{}.json".format(raw_pid)
                raw_problem = load_json(path_problems + filename)
                timing = time.time()
                solver.load_problem(raw_problem)
                for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(raw_problem["theorem_seqs"]):
                    solver.apply_theorem(t_name, t_branch, t_para)
                solver.problem.check_goal()  # check goal after applied theorem seqs
                simple_show(raw_pid, solver.problem.goal.answer, solver.problem.goal.solved,
                            solver.problem.goal.solved_answer, time.time() - timing, raw_pid)  # show solved msg
                augment_data = load_json(path_problems_augment + filename)
            except BaseException as e:
                error_problems.append((raw_pid, raw_pid, repr(e)))
                continue

            for pid in augment_data:
                timing = time.time()
                try:  # try solve
                    problem_CDL = assemble(raw_problem, augment_data[pid])
                    solver.load_problem(problem_CDL)

                    for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(problem_CDL["theorem_seqs"]):
                        solver.apply_theorem(t_name, t_branch, t_para)

                    solver.problem.check_goal()  # check goal after applied theorem seqs

                    if not show_solved and solver.problem.goal.solved:
                        continue
                    simple_show(pid, solver.problem.goal.answer, solver.problem.goal.solved,
                                solver.problem.goal.solved_answer, time.time() - timing, raw_pid)  # show solved msg

                except Exception as e:  # exception
                    error_problems.append((raw_pid, pid, repr(e)))

        print("\nraw_pid\tpid\te_msg")
        for raw_pid, pid, e_msg in error_problems:  # show unsolved
            print("{}\t{}\t{}".format(raw_pid, pid, e_msg))

    else:  # interactive mode, run one problem according input pid
        while True:
            try:
                raw_pid, pid = input("<raw_pid pid>:").split(" ")
                filename = "{}.json".format(raw_pid)
                raw_problem = load_json(path_problems + filename)
                augment_problem = load_json(path_problems_augment + filename)[pid]
                problem_CDL = assemble(raw_problem, augment_problem)
            except BaseException as e:
                print(repr(e) + "\n")
                continue

            solver.load_problem(problem_CDL)

            for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(problem_CDL["theorem_seqs"]):
                solver.apply_theorem(t_name, t_branch, t_para)

            solver.problem.check_goal()  # check goal after applied theorem seqs

            show(solver.problem)  # show solving process


def check_search(direction, method, auto=False, start_pid=1, end_pid=6981):
    """Run method and load problem from problem_GDL."""
    solver = Interactor(load_json(path_gdl + "predicate_GDL.json"),  # init method
                        load_json(path_gdl + "theorem_GDL.json"))
    search_data = load_json(path_search_data + "{}-{}.json".format(direction, method))["solved"]

    if auto:
        warnings.filterwarnings("ignore")
        error_problems = []
        print("pid\tcorrect_answer\tsolved\tsolved_answer\ttiming(s)")

        for pid in range(start_pid, end_pid + 1):
            timing = time.time()
            filename = "{}.json".format(pid)
            if str(pid) not in search_data:
                continue

            try:  # try solve
                problem_CDL = load_json(path_problems + filename)
                solver.load_problem(problem_CDL)

                for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(search_data[str(pid)]["msg"]):
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
            try:
                pid = input("pid:")
                filename = "{}.json".format(pid)
                problem_CDL = load_json(path_problems + filename)
                theorem_seqs = search_data[str(pid)]["msg"]
            except BaseException as e:
                print(repr(e) + "\n")
                continue

            solver.load_problem(problem_CDL)

            for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(theorem_seqs):
                solver.apply_theorem(t_name, t_branch, t_para)

            solver.problem.check_goal()  # check goal after applied theorem seqs

            show(solver.problem)  # show solving process


if __name__ == '__main__':
    # check_raw(auto=True)
    check_augment(auto=True, show_solved=False)
    # check_search(direction="fw", method="bfs", auto=False)
