from formalgeo.solver import ForwardSearcher, BackwardSearcher
from formalgeo.tools import load_json, save_json, safe_save_json
from formalgeo.data import DatasetLoader
from fgps import method, strategy, get_args
from multiprocessing import Process, Queue
from func_timeout import func_timeout, FunctionTimedOut
import random
import warnings
import os
import time
import psutil


def init_search_log(args, dl):
    data = {"solved": {}, "unsolved": {}, "timeout": {}, "error": {}}
    log = {"start_pid": 1, "end_pid": dl.info["problem_number"], "solved_pid": [], "unsolved_pid": [],
           "timeout_pid": [], "error_pid": []}

    log_filename = os.path.join(
        args.path_logs, "search", "{}-log-{}-{}.json".format(args.dataset_name, args.method, args.strategy))
    data_filename = os.path.join(
        args.path_logs, "search", "{}-data-{}-{}.json".format(args.dataset_name, args.method, args.strategy))

    if log_filename not in os.listdir(os.path.join(args.path_logs, "search")):
        save_json(log, log_filename)
        save_json(data, data_filename)

    return log_filename, data_filename


def sort_search_result(args):
    print("direction\tmethod\tunhandled")
    for m in method:
        for s in strategy:
            unhandled = []
            log_filename = os.path.join(args.path_logs, "search", "{}-log-{}-{}.json".format(args.dataset_name, m, s))
            data_filename = os.path.join(args.path_logs, "search", "{}-data-{}-{}.json".format(args.dataset_name, m, s))
            log = load_json(log_filename)
            data = load_json(data_filename)
            new_log = {"start_pid": 1, "end_pid": log["end_pid"],
                       "solved_pid": [], "unsolved_pid": [], "timeout_pid": [], "error_pid": []}
            new_data = {"solved": {}, "unsolved": {}, "timeout": {}, "error": {}}

            for pid in range(1, log["end_pid"] + 1):
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
            safe_save_json(new_log, log_filename)
            safe_save_json(new_data, data_filename)

            print("{}\t{}\t({}){}".format(m, s, len(unhandled), unhandled))


def solve(args, dl, problem_id, reply_queue, debug=False):
    """
    Start a process to solve problem.
    :param args: <argparse>, (args.method, args.strategy, args.max_depth, args.beam_size, args.timeout).
    :param problem_id: <int>, problem id.
    :param dl: <DatasetLoader>, use dl loading predicate_GDL, theorem_GDL and t_info.
    :param reply_queue: <Queue>, return solved result through this queue.
    :param debug: <Bool>, debug output.
    """
    warnings.filterwarnings("ignore")
    random.seed(args.random_seed)
    if args.method == "fw":
        searcher = ForwardSearcher(
            dl.predicate_GDL, dl.theorem_GDL,
            args.strategy, args.max_depth, args.beam_size,
            load_json(os.path.join(dl.dataset_path, "files/t_info.json")),
            debug=debug
        )
    else:
        searcher = BackwardSearcher(
            dl.predicate_GDL, dl.theorem_GDL,
            args.strategy, args.max_depth, args.beam_size,
            load_json(os.path.join(dl.dataset_path, "files/t_info.json")),
            debug=debug
        )

    timing = time.time()
    try:
        searcher.init_search(dl.get_problem(problem_id))
        solved, seqs = func_timeout(args.timeout, searcher.search())
        if solved:
            reply_queue.put((os.getpid(), problem_id, "solved", seqs, time.time() - timing, searcher.step_size))
        else:
            reply_queue.put((os.getpid(), problem_id, "unsolved", "None", time.time() - timing, searcher.step_size))
    except FunctionTimedOut:
        reply_queue.put(
            (os.getpid(), problem_id, "timeout", str(args.timeout), time.time() - timing, searcher.step_size))
    except BaseException as e:
        reply_queue.put((os.getpid(), problem_id, "error", repr(e), time.time() - timing, searcher.step_size))


def start_process(args, dl, problem_ids, process_ids, reply_queue):
    """Remove non-existent pid and start new process"""
    while len(problem_ids) > 0 and args.process_count - len(process_ids) > 0:
        problem_id = problem_ids.pop()
        process = Process(target=solve, args=(args, dl, problem_id, reply_queue))
        process.start()
        process_ids.append(process.pid)


def clean_process(process_ids):
    for i in range(len(process_ids))[::-1]:
        if process_ids[i] not in psutil.pids():
            process_ids.pop(i)


def search(args):
    """Auto run search on all problems."""
    dl = DatasetLoader(args.dataset_name, args.path_datasets)
    log_filename, data_filename = init_search_log(args, dl)
    log = load_json(log_filename)
    data = load_json(data_filename)
    problem_ids = []  # problem id
    process_ids = []  # process id

    reply_queue = Queue()

    for problem_id in range(log["start_pid"], log["end_pid"] + 1):  # assign tasks
        if problem_id in log["solved_pid"] or problem_id in log["unsolved_pid"] or \
                problem_id in log["timeout_pid"] or problem_id in log["error_pid"]:
            continue
        problem_ids.append(problem_id)
    problem_ids = problem_ids[::-1]

    clean_count = 0
    print("process_id\tproblem_id\tresult\tmsg")
    while True:
        start_process(args, dl, problem_ids, process_ids, reply_queue)  # search

        process_id, problem_id, result, msg, timing, step_size = reply_queue.get()
        data[result][str(problem_id)] = {"msg": msg, "timing": timing, "step_size": step_size}
        log["{}_pid".format(result)].append(problem_id)
        safe_save_json(log, log_filename)
        safe_save_json(data, data_filename)
        print("{}\t{}\t{}\t{}".format(process_id, problem_id, result, msg))

        if process_id in process_ids:
            process_ids.pop(process_ids.index(process_id))
        clean_count += 1
        if clean_count == int(args.process_count / 3):
            clean_process(process_ids)
            clean_count = 0


if __name__ == '__main__':
    search(get_args())
    # random.seed(619)
    # warnings.filterwarnings("ignore")
    # dl = DatasetLoader("formalgeo-imo_v1", "F:/Datasets/released/")
    # searcher = ForwardSearcher(
    #     dl.predicate_GDL, dl.theorem_GDL,
    #     "bfs", 60, 30,
    #     load_json(os.path.join(dl.dataset_path, "files/t_info.json")),
    #     debug=False
    # )
    # searcher.init_search(dl.get_problem(3))
    # solved, seqs = func_timeout(3600, searcher.search())

