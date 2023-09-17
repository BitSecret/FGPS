from solver.aux_tools.utils import load_json
from init_search import direction, method
from utils.utils import safe_save_json

path_search_data = "../../datasets/solved/search/"


def clean_error(error_name):
    """error_name=[KeyError, RuntimeError, MemoryError]"""
    for d in direction:
        for m in method:
            log = load_json("{}-{}.json".format(d, m))
            data = load_json(path_search_data + "{}-{}.json".format(d, m))
            for pid in data["error"]:
                if data["error"][pid]["msg"].startswith(error_name):
                    data["error"].pop(pid)
                    log["error_pid"].pop(int(pid))

            safe_save_json(log, "", "{}-{}".format(d, m))
            safe_save_json(data, path_search_data, "{}-{}".format(d, m))


def clean_timeout(timeout):
    timeout = str(timeout)
    for d in direction:
        for m in method:
            log = load_json("{}-{}.json".format(d, m))
            data = load_json(path_search_data + "{}-{}.json".format(d, m))
            for pid in data["timeout"]:
                if data["timeout"][pid]["msg"] == timeout:
                    data["timeout"].pop(pid)
                    log["timeout_pid"].pop(int(pid))

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


if __name__ == '__main__':
    clean_error("KeyError")
