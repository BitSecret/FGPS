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


def show_unhandled():
    print("direction\tmethod\tunhandled")
    for d in direction:
        for m in method:
            unhandled = []
            log = load_json("{}-{}.json".format(d, m))
            for pid in range(1, 6982):
                if pid in log["solved_pid"]:
                    continue
                if pid in log["unsolved_pid"]:
                    continue
                if pid in log["error_pid"]:
                    continue
                if pid in log["timeout_pid"]:
                    continue
                unhandled.append(pid)

            print("{}\t{}\t{}".format(d, m, unhandled))


if __name__ == '__main__':
    # clean_error(error_msg="RuntimeError(\"can't start new thread\")")
    # clean_error(error_msg="TypeError")
    clean_timeout()
    # clean_unsolved()
    show_unhandled()
