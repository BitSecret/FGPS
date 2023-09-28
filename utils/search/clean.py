from solver.aux_tools.utils import load_json
from init_search import direction, method
from utils.utils import safe_save_json

path_search_data = "../../datasets/solved/search/"


def clean_error(error_msg):
    """error_name: [KeyError, RuntimeError, MemoryError, TypeError, IndexError, KeyboardInterrupt]"""
    for d in direction:
        for m in method:
            log = load_json("{}-{}.json".format(d, m))
            data = load_json(path_search_data + "{}-{}.json".format(d, m))
            pop_pids = []
            for pid in data["error"]:
                if data["error"][pid]["msg"].startswith(error_msg):
                    pop_pids.append(pid)
            for pid in pop_pids:
                data["error"].pop(pid)
                log["error_pid"].pop(log["error_pid"].index(int(pid)))

            safe_save_json(log, "", "{}-{}".format(d, m))
            safe_save_json(data, path_search_data, "{}-{}".format(d, m))


def clean_timeout():
    for d in direction:
        for m in method:
            log = load_json("{}-{}.json".format(d, m))
            data = load_json(path_search_data + "{}-{}.json".format(d, m))
            data["timeout"] = {}
            log["timeout_pid"] = []
            safe_save_json(log, "", "{}-{}".format(d, m))
            safe_save_json(data, path_search_data, "{}-{}".format(d, m))


def clean_unsolved():
    for d in direction:
        for m in method:
            log = load_json("{}-{}.json".format(d, m))
            data = load_json(path_search_data + "{}-{}.json".format(d, m))
            data["unsolved"] = {}
            log["unsolved_pid"] = []
            safe_save_json(log, "", "{}-{}".format(d, m))
            safe_save_json(data, path_search_data, "{}-{}".format(d, m))


def in_order():
    print("direction\tmethod\tunhandled")
    for d in direction:
        for m in method:
            unhandled = []
            data = load_json(path_search_data + "{}-{}.json".format(d, m))
            new_data = {"solved": {}, "unsolved": {}, "timeout": {}, "error": {}}
            new_log = {"start_pid": 1, "end_pid": 6981,
                       "solved_pid": [], "unsolved_pid": [], "timeout_pid": [], "error_pid": []}
            for pid in range(1, 6982):
                if str(pid) in data["solved"]:
                    new_data["solved"][str(pid)] = data["solved"][str(pid)]
                    new_log["solved_pid"].append(pid)
                elif str(pid) in data["unsolved"]:
                    new_data["unsolved"][str(pid)] = data["unsolved"][str(pid)]
                    new_log["unsolved_pid"].append(pid)
                elif str(pid) in data["error"]:
                    new_data["error"][str(pid)] = data["error"][str(pid)]
                    new_log["error_pid"].append(pid)
                elif str(pid) in data["timeout"]:
                    new_data["timeout"][str(pid)] = data["timeout"][str(pid)]
                    new_log["timeout_pid"].append(pid)
                else:
                    unhandled.append(pid)
            safe_save_json(new_data, path_search_data, "{}-{}".format(d, m))
            safe_save_json(new_log, "", "{}-{}".format(d, m))

            print("{}\t{}\t{}".format(d, m, unhandled))


if __name__ == '__main__':
    # clean_error(error_msg="TypeError")
    # clean_timeout()
    # clean_unsolved()
    in_order()
