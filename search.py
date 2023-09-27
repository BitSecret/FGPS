from multiprocessing import Process, Queue
from solver.method.forward_search import ForwardSearcher
from solver.method.backward_search import BackwardSearcher
from solver.aux_tools.utils import load_json, search_timout
from utils.utils import safe_save_json
from func_timeout import FunctionTimedOut
import argparse
import warnings
import os
import time
import psutil

process_count = int(psutil.cpu_count() * 0.8)
path_gdl = "datasets/gdl/"
path_problems = "datasets/problems/"
path_search_data = "datasets/solved/search/"
path_search_log = "utils/search/"


def get_args():
    """python search.py --direction fw --method bfs --max_depth 10 --beam_size 10"""
    parser = argparse.ArgumentParser(description="Welcome to use FormalGeo Searcher!")

    parser.add_argument("--direction", type=str, required=True, choices=("fw", "bw"), help="search direction")
    parser.add_argument("--method", type=str, required=True, choices=("bfs", "dfs", "rs", "bs"), help="search method")
    parser.add_argument("--max_depth", type=int, required=True, help="max search depth")
    parser.add_argument("--beam_size", type=int, required=True, help="search beam size")

    return parser.parse_args()


def solve(search_config, problem_id, reply_queue):
    """
    Start a process to solve problem.
    :param search_config: <tuple>, direction("fw", "bw"), method("dfs", "bfs", "rs", "bs"), max_depth, beam_size.
    :param problem_id: <int>, problem.
    :param reply_queue: <Queue>, return solved result through this queue.
    """
    direction, method, max_depth, beam_size = search_config
    warnings.filterwarnings("ignore")
    if direction == "fw":
        searcher = ForwardSearcher(
            load_json(path_gdl + "predicate_GDL.json"), load_json(path_gdl + "theorem_GDL.json"),
            method=method, max_depth=max_depth, beam_size=beam_size,
            p2t_map=load_json(path_search_log + "p2t_map-fw.json")
        )
    else:
        searcher = BackwardSearcher(
            load_json(path_gdl + "predicate_GDL.json"), load_json(path_gdl + "theorem_GDL.json"),
            method=method, max_depth=max_depth, beam_size=beam_size,
            p2t_map=load_json(path_search_log + "p2t_map-bw.json")
        )

    timeout = str(search_timout)
    timing = time.time()
    try:
        searcher.init_search(load_json(path_problems + "{}.json".format(problem_id)))
        solved, seqs = searcher.search()
        if solved:
            reply_queue.put((os.getpid(), problem_id, "solved", seqs, time.time() - timing, searcher.step_size))
        else:
            reply_queue.put((os.getpid(), problem_id, "unsolved", "None", time.time() - timing, searcher.step_size))
    except FunctionTimedOut:
        reply_queue.put((os.getpid(), problem_id, "timeout", timeout, time.time() - timing, searcher.step_size))
    except BaseException as e:
        reply_queue.put((os.getpid(), problem_id, "error", repr(e), time.time() - timing, searcher.step_size))


def start_process(search_config, problem_ids, process_ids, reply_queue):
    """Remove non-existent pid and start new process"""
    while len(problem_ids) > 0 and process_count - len(process_ids) > 0:
        problem_id = problem_ids.pop()
        process = Process(target=solve, args=(search_config, problem_id, reply_queue))
        process.start()
        process_ids.append(process.pid)


def clean_process(process_ids):
    for i in range(len(process_ids))[::-1]:
        if process_ids[i] not in psutil.pids():
            process_ids.pop(i)


def auto(search_config):
    """Auto run search on all problems."""
    filename = "{}-{}.json".format(search_config[0], search_config[1])
    log = load_json(path_search_log + filename)
    data = load_json(path_search_data + filename)
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
    print("process_id\tproblem_id\tresult\tmsg\t")
    while True:
        start_process(search_config, problem_ids, process_ids, reply_queue)  # run multiprocess

        process_id, problem_id, result, msg, timing, step_size = reply_queue.get()
        data[result][str(problem_id)] = {"msg": msg, "timing": timing, "step_size": step_size}
        log["{}_pid".format(result)].append(problem_id)
        safe_save_json(log, path_search_log, "{}-{}".format(search_config[0], search_config[1]))
        safe_save_json(data, path_search_data, "{}-{}".format(search_config[0], search_config[1]))
        print("{}\t{}\t{}\t{}".format(process_id, problem_id, result, msg))

        process_ids.pop(process_ids.index(process_id))
        clean_count += 1
        if clean_count == int(process_count / 3):
            clean_process(process_ids)
            clean_count = 0


if __name__ == '__main__':
    args = get_args()
    auto((args.direction, args.method, args.max_depth, args.beam_size))
