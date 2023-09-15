from solver.aux_tools.utils import load_json, save_json

path_problems_augment = "../../datasets/problems-augment/"
pid_count = 6982

for pid in range(1, 6982):
    filename = "{}.json".format(pid)
    data = load_json(path_problems_augment + filename)
    new_data = {}
    for old_pid in data:
        new_data[pid_count] = data[old_pid]
        new_data[pid_count]["problem_id"] = pid_count
        pid_count += 1
    save_json(new_data, path_problems_augment + filename)
