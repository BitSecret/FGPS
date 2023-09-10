import random
import time
import os
import errno
from multiprocessing import Process, Queue, current_process
from solver.aux_tools.utils import load_json
from utils.utils import safe_save_json
from solver.method.interactive import Interactor
from solver.method.forward_search import ForwardSearcher
from solver.method.backward_search import BackwardSearcher
from solver.aux_tools.utils import *
from solver.aux_tools.output import *
from solver.aux_tools.parser import CDLParser
from solver.core.engine import EquationKiller as EqKiller
from func_timeout import FunctionTimedOut
import warnings
import os
import argparse

cpu_core = 6  # cpu core
path_gdl = "datasets/gdl/"
path_problems = "datasets/problems/"
path_search_data = "datasets/search/"
path_search_log = "utils/search/"


def process_exits(pid):
    """Check if the process exists."""
    try:
        os.kill(pid, 0)
    except OSError as e:
        return False
    return True


def start_process(direction, method, pool, task_queue, reply_queue):
    """Remove non-existent pid and start new process"""
    for i in range(len(pool))[::-1]:  # remove non-existent pid
        if not process_exits(pool[i]):
            pool.pop(i)

    if not task_queue.empty():  # start new process
        for i in range(cpu_core - len(pool)):
            process = Process(target=solve, args=(direction, method, task_queue, reply_queue))
            process.start()
            pool.append(process.pid)


def solve(direction, method, task_queue, reply_queue):
    """
    Start a process to solve problem.
    :param direction: <str>, "fw", "bw".
    :param method: <str>, "dfs", "bfs", "rs", "bs".
    :param task_queue: <Queue>, get task id through this queue.
    :param reply_queue: <Queue>, return solved result through this queue.
    """

    while True:
        problem_id = task_queue.get()
        time.sleep(task)
        reply_queue.put((pid, task_id, task))


def auto(direction, method):
    """Auto run search on all problems."""
    filename = "{}-{}.json".format(direction, method)
    log = load_json(path_search_log + filename)
    data = load_json(path_search_data + filename)
    pool = []    # save process_id

    task_queue = Queue()
    reply_queue = Queue()

    for problem_id in range(log["start_pid"], log["6981"] + 1):  # assign tasks
        if problem_id in log["solved_pid"] or problem_id in log["unsolved_pid"] or problem_id in log["error_pid"]:
            continue
        task_queue.put(problem_id)

    print("process_id\tproblem_id\tresult\tmsg")
    while True:  # run process and
        start_process(direction, method, pool, task_queue, reply_queue)
        if len(pool) == 0:    # no unhandled problem
            break

        process_id, problem_id, result, msg, timing, step_size = reply_queue.get()
        data[str(problem_id)] = {
            "result": result,
            "msg": msg,
            "timing": timing,
            "step_size": step_size
        }
        if result == "solved":
            log["solved_pid"].append(problem_id)
        elif result == "unsolved":
            log["unsolved_pid"].append(problem_id)
        else:
            log["error_pid"].append(problem_id)
        safe_save_json(log, path_search_log, "{}-{}".format(direction, method))
        safe_save_json(data, path_search_data, "{}-{}".format(direction, method))

        print("{}\t{}\t{}\t{}".format(process_id, problem_id, result, msg))


def run(direction, method):
    """Run one problem by search"""
    warnings.filterwarnings("ignore")

    if direction == "fw":  # init searcher
        searcher = ForwardSearcher(
            load_json(path_gdl + "predicate_GDL.json"), load_json(path_gdl + "theorem_GDL.json"),
            max_depth=5, beam_size=10, method=method, debug=True
        )
        while True:
            pid = input("pid:")
            filename = "{}.json".format(pid)
            if filename not in os.listdir(path_problems):
                print("No file \'{}\' in \'{}\'.\n".format(filename, path_problems))
                continue
            searcher.init_problem(load_json(path_problems + filename))
            solved, seqs = searcher.search()

            print("pid: {}  solved: {}  seqs:{}\n".format(pid, solved, seqs))
    else:
        searcher = BackwardSearcher(
            load_json(path_gdl + "predicate_GDL.json"), load_json(path_gdl + "theorem_GDL.json"),
            max_depth=5, beam_size=10, method=method, debug=True
        )






if __name__ == '__main__':
    run(direction="fw", method="dfs")
    auto(direction="fw", method="dfs")
