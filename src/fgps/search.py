from formalgeo.solver import ForwardSearcher, BackwardSearcher
from formalgeo.tools import load_json, save_json, safe_save_json
from formalgeo.data import DatasetLoader
from multiprocessing import Process, Queue
from func_timeout import func_timeout, FunctionTimedOut
import random
import argparse
import warnings
import os
import time
import psutil

direction = ["fw", "bw"]  # forward, backward
method = ["bfs", "dfs", "rs", "bs"]  # deep first, breadth first, random, beam


def init_search(file_path):
    data = {"solved": {}, "unsolved": {}, "timeout": {}, "error": {}}
    log = {"start_pid": 1, "end_pid": 6981, "solved_pid": [], "unsolved_pid": [], "timeout_pid": [], "error_pid": []}
    for d in direction:
        for m in method:
            save_json(log, os.path.join(file_path, "log-{}-{}.json".format(d, m)))
            save_json(data, os.path.join(file_path, "data-{}-{}.json".format(d, m)))


def get_args():
    """python search.py --direction fw --method bfs"""
    parser = argparse.ArgumentParser(description="Welcome to use FormalGeo Searcher!")

    parser.add_argument("--datasets_path", type=str, required=True, help="datasets path")
    parser.add_argument("--direction", type=str, required=True, choices=("fw", "bw"), help="search direction")
    parser.add_argument("--method", type=str, required=True, choices=("bfs", "dfs", "rs", "bs"), help="search method")
    parser.add_argument("--max_depth", type=int, required=False, default=15, help="max search depth")
    parser.add_argument("--beam_size", type=int, required=False, default=20, help="search beam size")
    parser.add_argument("--timeout", type=int, required=False, default=300, help="search timeout")
    parser.add_argument("--process_count", type=int, required=False, default=int(psutil.cpu_count() * 0.8),
                        help="multi process count")
    parser.add_argument("--file_path", type=str, required=False, default="./search_log",
                        help="file that save search result")
    parser.add_argument("--random_seed", type=int, required=False, default=619, help="random seed")

    return parser.parse_args()


def solve(args, dl, problem_id, reply_queue):
    """
    Start a process to solve problem.
    :param args: <argparse>, (args.direction, args.method, args.max_depth, args.beam_size, args.timeout).
    :param problem_id: <int>, problem id.
    :param dl: <DatasetLoader>, use dl loading predicate_GDL, theorem_GDL and t_info.
    :param reply_queue: <Queue>, return solved result through this queue.
    """
    warnings.filterwarnings("ignore")
    random.seed(args.random_seed)
    if args.direction == "fw":
        searcher = ForwardSearcher(
            dl.predicate_GDL, dl.theorem_GDL,
            args.method, args.max_depth, args.beam_size,
            load_json(os.path.join(dl.datasets_path, "files/t_info.json"))
        )
    else:
        searcher = BackwardSearcher(
            dl.predicate_GDL, dl.theorem_GDL,
            args.method, args.max_depth, args.beam_size,
            load_json(os.path.join(dl.datasets_path, "files/t_info.json"))
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
    if not os.path.exists(args.file_path):
        os.makedirs(args.file_path)
        init_search(args.file_path)
    dl = DatasetLoader("formalgeo7k_v1", args.datasets_path)
    log_filename = os.path.join(args.file_path, "log-{}-{}.json".format(args.direction, args.method))
    data_filename = os.path.join(args.file_path, "data-{}-{}.json".format(args.direction, args.method))
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
