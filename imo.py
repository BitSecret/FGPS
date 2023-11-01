from solver.method.interactive import Interactor
from solver.aux_tools.utils import load_json, save_json
from solver.aux_tools.output import show
from solver.aux_tools.parser import CDLParser
from solver.aux_tools.output import get_used

path_gdl = "datasets/gdl/"
path_problems = "datasets/problems-imo/"

if __name__ == '__main__':
    solver = Interactor(load_json(path_gdl + "predicate_GDL.json"),  # init method
                        load_json(path_gdl + "theorem_GDL.json"))
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
        if solver.problem.goal.solved:
            _, theorem_seqs = get_used(solver.problem)  # clean theorem seqs
            problem_CDL["theorem_seqs"] = theorem_seqs
            save_json(problem_CDL, path_problems + filename)

        show(solver.problem)  # show solving process
