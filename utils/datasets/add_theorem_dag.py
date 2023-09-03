import os
from solver.aux_tools.utils import load_json, save_json

solved_path = "../../datasets/solved/"
problems_path = "../../datasets/problems/"


def main(start_pid, end_pid):
    solved_files = os.listdir(solved_path)
    for pid in range(start_pid, end_pid + 1):
        if "{}_dag.json".format(pid) not in solved_files:
            continue
        dag = load_json(solved_path + "{}_dag.json".format(pid))
        problem = load_json(problems_path + "{}.json".format(pid))
        if "theorem_seq_dag" not in problem:
            problem["theorem_seq_dag"] = dag
        save_json(problem, problems_path + "{}.json".format(pid))


if __name__ == '__main__':
    main(start_pid=1, end_pid=6981)
