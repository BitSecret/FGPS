from utils.search.init_search import direction, method
from solver.aux_tools.utils import load_json

path_problems = "../../datasets/problems/"
path_search_data = "../../datasets/solved/search/"
path_search_log = "../search/"


def roughly():
    print("direction\tmethod\tsolved\tunsolved\ttimeout\terror")
    for d in direction:
        for m in method:
            data = load_json(path_search_log + "{}-{}.json".format(d, m))
            solved = len(data["solved_pid"])
            unsolved = len(data["unsolved_pid"])
            timeout = len(data["timeout_pid"])
            error = len(data["error_pid"])
            total = solved + unsolved + timeout + error
            if total == 0:
                continue
            print("{}\t{}\t{}/{}({:.2f}%)\t{}/{}({:.2f}%)\t{}/{}({:.2f}%)\t{}/{}({:.2f}%)\t".format(
                d, m, solved, total, solved / total * 100, unsolved, total, unsolved / total * 100,
                timeout, total, timeout / total * 100, error, total, error / total * 100))


def detailed():
    pid_map = {}  # map pid to column
    config_map = {}  # map config tp row

    for pid in range(1, 6982):
        problem_CDL = load_json(path_problems + "{}.json".format(pid))
        t_length = len(problem_CDL["theorem_seqs"])
        if t_length <= 3:
            pid_map[pid] = 1
        elif t_length <= 6:
            pid_map[pid] = 2
        elif t_length <= 9:
            pid_map[pid] = 3
        elif t_length <= 12:
            pid_map[pid] = 4
        elif t_length <= 15:
            pid_map[pid] = 5
        else:
            pid_map[pid] = 6

    count = 0
    for d in direction:
        for m in method:
            config_map[(d, m)] = count
            count += 1

    solving = [[[0, 0]] * 7 for i in range(8)]  # [count(S), count(U)]
    timing = [[[0, 0]] * 7 for i in range(8)]  # [item(S), item(U)]
    step_size = [[[0, 0]] * 7 for i in range(8)]  # [item(S), item(U)]

    for d in direction:
        for m in method:
            search_data = load_json(path_search_data + "{}-{}.json".format(d, m))
            search_data["unsolved"].update(search_data["timeout"])
            search_data["unsolved"].update(search_data["error"])
            search_data.pop("timeout")
            search_data.pop("error")
            i = config_map[(d, m)]

            for pid in range(1, 6982):
                j = pid_map[pid]
                k = 0 if str(pid) in search_data["solved"] else 1
                problem_data = search_data["solved"][str(pid)] if k == 0 else search_data["unsolved"][str(pid)]

                solving[i][j][k] += 1
                timing[i][j][k] += problem_data["timing"]
                step_size[i][j][k] += problem_data["step_size"]

    for d in direction:
        for m in method:
            i = config_map[(d, m)]
            for j in range(1, 7):
                for k in range(2):
                    solving[i][0][k] += solving[i][j][k]
                    timing[i][0][k] += timing[i][j][k]
                    step_size[i][0][k] += step_size[i][j][k]
    print("config\ttotal\tl<=3\t4<=l<=6\t7<=l<=9\t10<=l<=12\t13<=l<=15\tl>=16")


if __name__ == '__main__':
    roughly()
    # detailed()
