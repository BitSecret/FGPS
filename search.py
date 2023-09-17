from multiprocessing import Process, Queue
from solver.method.forward_search import ForwardSearcher, fw_timeout
from solver.method.backward_search import BackwardSearcher, bw_timeout
from solver.aux_tools.utils import load_json
from utils.utils import safe_save_json
from func_timeout import FunctionTimedOut
import argparse
import warnings
import os
import psutil
import time

process_count = 10  # logical cpu core - 2
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


def start_process(direction, method, max_depth, beam_size, pool, task_queue, reply_queue):
    """Remove non-existent pid and start new process"""
    for i in range(len(pool))[::-1]:  # remove non-existent pid
        if pool[i] not in psutil.pids():
            pool.pop(i)
        else:
            process = psutil.Process(os.getpid())
            memory = process.memory_info().rss / (1024 * 1024)
            cpu_times = process.cpu_times().user
            if memory > 300 or cpu_times > 2000:
                process.terminate()
                pool.pop(i)

    if not task_queue.empty():  # start new process
        for i in range(process_count - len(pool)):
            process = Process(target=solve, args=(direction, method, max_depth, beam_size, task_queue, reply_queue))
            process.start()
            pool.append(process.pid)


def solve(direction, method, max_depth, beam_size, task_queue, reply_queue):
    """
    Start a process to solve problem.
    :param direction: <str>, "fw", "bw".
    :param method: <str>, "dfs", "bfs", "rs", "bs".
    :param max_depth: max search depth.
    :param beam_size: beam search size.
    :param task_queue: <Queue>, get task id through this queue.
    :param reply_queue: <Queue>, return solved result through this queue.
    """
    warnings.filterwarnings("ignore")
    if direction == "fw":
        searcher = ForwardSearcher(
            load_json(path_gdl + "predicate_GDL.json"), load_json(path_gdl + "theorem_GDL.json"),
            method=method, max_depth=max_depth, beam_size=beam_size,
            p2t_map=load_json(path_search_log + "p2t_map-fw.json")
        )
        timeout = str(fw_timeout)
    else:
        searcher = BackwardSearcher(
            load_json(path_gdl + "predicate_GDL.json"), load_json(path_gdl + "theorem_GDL.json"),
            method=method, max_depth=max_depth, beam_size=beam_size,
            p2t_map=load_json(path_search_log + "p2t_map-bw.json")
        )
        timeout = str(bw_timeout)

    for i in range(5):  # Restart after processing 5 tasks to prevent memory explosion
        if task_queue.empty():
            break
        problem_id = task_queue.get()
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


def auto(direction, method, max_depth, beam_size):
    """Auto run search on all problems."""
    filename = "{}-{}.json".format(direction, method)
    log = load_json(path_search_log + filename)
    data = load_json(path_search_data + filename)
    pool = []  # process id
    task_count = 0  # problem id

    task_queue = Queue()
    reply_queue = Queue()

    for problem_id in range(log["start_pid"], log["end_pid"] + 1):  # assign tasks
        if problem_id in log["solved_pid"] or problem_id in log["unsolved_pid"] or \
                problem_id in log["timeout_pid"] or problem_id in log["error_pid"]:
            continue
        task_queue.put(problem_id)
        task_count += 1

    while True:
        start_process(direction, method, max_depth, beam_size, pool, task_queue, reply_queue)  # run process

        process_id, problem_id, result, msg, timing, step_size = reply_queue.get()
        data[result][str(problem_id)] = {"msg": msg, "timing": timing, "step_size": step_size}
        log["{}_pid".format(result)].append(problem_id)
        safe_save_json(log, path_search_log, "{}-{}".format(direction, method))
        safe_save_json(data, path_search_data, "{}-{}".format(direction, method))

        print("process_id={}, problem_id={}, result={}, msg={}".format(process_id, problem_id, result, msg))

        task_count -= 1  # exit when all problem has been handled.
        if task_count == 0:
            break


if __name__ == '__main__':
    args = get_args()
    auto(direction=args.direction, method=args.method, max_depth=args.max_depth, beam_size=args.beam_size)
    # auto(direction="fw", method="bfs", max_depth=10, beam_size=10)
