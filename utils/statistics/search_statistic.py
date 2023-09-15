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


if __name__ == '__main__':
    roughly()
