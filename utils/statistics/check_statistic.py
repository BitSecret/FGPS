from solver.method.interactive import Interactor
from solver.aux_tools.utils import load_json
from solver.aux_tools.output import show
from solver.aux_tools.parser import CDLParser
from utils.augment.get_data_aug import assemble
import warnings
import time

path_gdl = "../../datasets/gdl/"
path_problems = "../../datasets/problems/"
path_problems_augment = "../../datasets/problems-augment/"


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


def check_raw(start_pid=1, end_pid=6981):
    """Run method and load problem from problem_GDL."""
    timing = {}  # {len(theorem): [timing_total, count]}
    solver = Interactor(load_json(path_gdl + "predicate_GDL.json"),  # init method
                        load_json(path_gdl + "theorem_GDL.json"))
    warnings.filterwarnings("ignore")
    print("pid\tcorrect_answer\tsolved\tsolved_answer\ttiming(s)")
    for pid in range(start_pid, end_pid + 1):
        start_time = time.time()
        filename = "{}.json".format(pid)
        problem_CDL = load_json(path_problems + filename)
        solver.load_problem(problem_CDL)
        l = len(problem_CDL["theorem_seqs"])
        for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(problem_CDL["theorem_seqs"]):
            solver.apply_theorem(t_name, t_branch, t_para)
        solver.problem.check_goal()  # check goal after applied theorem seqs
        if l not in timing:
            timing[l] = [time.time() - start_time, 1]
        else:
            timing[l][0] += time.time() - start_time
            timing[l][1] += 1
        simple_show(pid, solver.problem.goal.answer, solver.problem.goal.solved,
                    solver.problem.goal.solved_answer, time.time() - start_time)  # show solved msg

    print("problem_level\ttiming\ttotal")
    for l in timing:
        print("{}\t{}\t{}".format(l, timing[l][0], timing[l][1]))


def check_augment(start_pid=1, end_pid=6981, show_solved=True):
    """Run method and load problem from problem_GDL."""
    timing = {}  # {len(theorem): [timing_total, count]}
    solver = Interactor(load_json(path_gdl + "predicate_GDL.json"),  # init method
                        load_json(path_gdl + "theorem_GDL.json"))

    warnings.filterwarnings("ignore")
    print("raw_pid\tpid\tcorrect_answer\tsolved\tsolved_answer\ttiming(s)")

    for raw_pid in range(start_pid, end_pid + 1):
        start_time = time.time()
        filename = "{}.json".format(raw_pid)
        raw_problem = load_json(path_problems + filename)
        solver.load_problem(raw_problem)
        l = len(raw_problem["theorem_seqs"])
        for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(raw_problem["theorem_seqs"]):
            solver.apply_theorem(t_name, t_branch, t_para)
        solver.problem.check_goal()  # check goal after applied theorem seqs
        if l not in timing:
            timing[l] = [time.time() - start_time, 1]
        else:
            timing[l][0] += time.time() - start_time
            timing[l][1] += 1
        simple_show(raw_pid, solver.problem.goal.answer, solver.problem.goal.solved,
                    solver.problem.goal.solved_answer, time.time() - start_time, raw_pid)  # show solved msg
        augment_data = load_json(path_problems_augment + filename)

        for pid in augment_data:
            start_time = time.time()
            problem_CDL = assemble(raw_problem, augment_data[pid])
            solver.load_problem(problem_CDL)
            l = len(problem_CDL["theorem_seqs"])
            for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(problem_CDL["theorem_seqs"]):
                solver.apply_theorem(t_name, t_branch, t_para)
            solver.problem.check_goal()  # check goal after applied theorem seqs
            if l not in timing:
                timing[l] = [time.time() - start_time, 1]
            else:
                timing[l][0] += time.time() - start_time
                timing[l][1] += 1
            if not show_solved and solver.problem.goal.solved:
                continue
            simple_show(pid, solver.problem.goal.answer, solver.problem.goal.solved,
                        solver.problem.goal.solved_answer, time.time() - start_time, raw_pid)  # show solved msg

    print("problem_level\ttiming\ttotal")
    for l in timing:
        print("{}\t{}\t{}".format(l, timing[l][0], timing[l][1]))


if __name__ == '__main__':
    # check_raw()
    check_augment()
