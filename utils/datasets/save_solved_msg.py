import copy
from utils.utils import safe_save_json
from solver.method.interactive import Interactor
from solver.aux_tools.utils import load_json, save_json
from solver.aux_tools.output import *
from solver.aux_tools.parser import CDLParser
import warnings

path_gdl = "../../datasets/gdl/"
path_problems = "../../datasets/problems/"
path_search = "../../datasets/search/"
path_solved = "../../datasets/solved/"


def add_theorem_dag(auto=False, start_pid=1, end_pid=6981):
    solved_files = os.listdir(path_solved)

    if auto:
        for pid in range(start_pid, end_pid + 1):
            if "{}_dag.json".format(pid) not in solved_files:
                continue
            dag = load_json(path_solved + "{}_dag.json".format(pid))
            problem = load_json(path_problems + "{}.json".format(pid))
            problem["theorem_seq_dag"] = dag
            save_json(problem, path_problems + "{}.json".format(pid))
            print("<AddTheoremDAG> Problem {} done.".format(pid))
    else:
        while True:
            pid = input("pid:")
            if "{}_dag.json".format(pid) not in solved_files:
                continue
            dag = load_json(path_solved + "{}_dag.json".format(pid))
            problem = load_json(path_problems + "{}.json".format(pid))
            problem["theorem_seq_dag"] = dag
            save_json(problem, path_problems + "{}.json".format(pid))
            print("<AddTheoremDAG> Problem {} done.".format(pid))


def save_gdl():
    """Save parsed GDL"""
    solver = Interactor(load_json(path_gdl + "predicate_GDL.json"),  # init method
                        load_json(path_gdl + "theorem_GDL.json"))
    save_json(solver.predicate_GDL, path_gdl + "predicate_parsed.json")
    save_json(solver.theorem_GDL, path_gdl + "theorem_parsed.json")


def main(auto=False, check_search=None, start_pid=1, end_pid=6981,
         save_parsed_cdl=False, save_step=False,
         save_hyper=False, save_hyper_pic=False, save_dag=False, save_dag_pic=False):
    solver = Interactor(load_json(path_gdl + "predicate_GDL.json"), load_json(path_gdl + "theorem_GDL.json"))
    search_data = {} if check_search is None else load_json(path_search + "{}.json".format(check_search))

    if auto:
        warnings.filterwarnings("ignore")
        error_problem = []  # (pid, timing, error), problems that raise Exception

        for pid in range(start_pid, end_pid + 1):
            timing = time.time()
            filename = "{}.json".format(pid)
            try:
                problem_CDL = load_json(path_problems + filename)  # get problem msg
                solver.load_problem(problem_CDL)
                if save_parsed_cdl:
                    save_json(solver.problem.problem_CDL, path_solved + "{}_parsed.json".format(pid))

                if check_search is None:
                    theorem_seqs = problem_CDL["theorem_seqs"]
                else:
                    theorem_seqs = search_data[str(pid)]

                for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(theorem_seqs):  # apply theorem seqs
                    solver.apply_theorem(t_name, t_branch, t_para)
                solver.problem.check_goal()
                if not solver.problem.goal.solved:
                    error_problem.append((pid, time.time() - timing, "Can't solve problem using given theorem seqs."))
                    continue

                if save_step:
                    save_step_msg(solver.problem, path_solved)
                save_solution_tree(solver.problem, path_solved, save_hyper, save_hyper_pic, save_dag, save_dag_pic)
                print("<SaveSolvedMsg> Problem {} done with timing {}s.".format(pid, time.time() - timing))

            except Exception as e:
                error_problem.append((pid, time.time() - timing, repr(e)))
                continue

        print("\n<SaveSolvedMsg> Error:")
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

            if save_parsed_cdl:
                save_json(solver.problem.problem_CDL, path_solved + "{}_parsed.json".format(pid))

            if check_search is None:
                theorem_seqs = problem_CDL["theorem_seqs"]
            else:
                theorem_seqs = search_data[str(pid)]

            for t_name, t_branch, t_para in CDLParser.parse_theorem_seqs(theorem_seqs):  # apply theorem seqs
                solver.apply_theorem(t_name, t_branch, t_para)
            solver.problem.check_goal()
            if not solver.problem.goal.solved:
                print("<SaveSolvedMsg> Can't solve problem using given theorem seqs.\n")
                continue

            if save_step:
                save_step_msg(solver.problem, path_solved)
            save_solution_tree(solver.problem, path_solved, save_hyper, save_hyper_pic, save_dag, save_dag_pic)
            print("<SaveSolvedMsg> Problem {} done with timing {}s.".format(pid, time.time() - timing))


if __name__ == '__main__':
    save_gdl()
    # main(auto=False, save_dag=True)
    # add_theorem_dag()
