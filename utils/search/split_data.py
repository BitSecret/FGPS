import os
from core.aux_tools.utils import load_json, save_json
formalized_path = "../../data/formalized-problems/"


def forward_search(split_count=6, direction="fw"):
    problem_count = 0
    if direction == "fw":
        search = "forward_search"
    else:
        search = "backward_search"

    for filename in os.listdir(formalized_path):
        problem_CDL = load_json(formalized_path + filename)
        if "notes" in problem_CDL or search in problem_CDL or int(filename.split(".")[0]) > 10000:
            continue
        problem_count += 1

    print("direction: {}".format(search))
    print("unsolved problem: {}".format(problem_count))
    print()

    split_problem_count = int(problem_count / split_count)
    results = []
    count = 0
    pid = 0
    for filename in os.listdir(formalized_path):
        problem_CDL = load_json(formalized_path + filename)
        if "notes" in problem_CDL or search in problem_CDL or int(filename.split(".")[0]) > 10000:
            continue
        pid = int(filename.split(".")[0])
        if count == 0:
            results.append([int(filename.split(".")[0])])
        count += 1
        if count == split_problem_count:
            results[-1].append(int(filename.split(".")[0]))
            count = 0

    if len(results) > split_count:
        results.pop(-1)
    results[-1][1] = pid

    print("conda activate FormalGeo")
    print("f:")
    print("cd FormalGeo")
    print()

    for start_pid, end_pid in results:
        print("python check.py --start_pid {} --end_pid {} --direction {}".format(start_pid, end_pid, direction))
    print()

    print("conda activate FormalGeo")
    print("f:")
    print("cd FormalGeo/useful/search")
    print("python dog.py")


if __name__ == '__main__':
    forward_search(split_count=6, direction="bw")

