import random
import time
import os
import errno
from multiprocessing import Process, Queue, current_process
from solver.aux_tools.utils import load_json
from utils.utils import safe_save_json
from solver.method.interactive import Interactor
from solver.method.forward_search import ForwardSearcher
# from solver.method.backward_search import BackwardSearcher
from solver.aux_tools.utils import *
from solver.aux_tools.output import *
from solver.aux_tools.parser import CDLParser, GDLParser
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
path_raw_gdl = "utils/gdl/"


def get_p2t_map():
    if "p2t_map.json" in os.listdir(path_search_log):
        return load_json(path_search_log + "p2t_map.json")

    t_msg = {}
    gdl = load_json(path_raw_gdl + "theorem.json")["Theorems"]
    for theorem in gdl:
        t_name = theorem.split("(", 1)[0]
        t_msg[t_name] = [gdl[theorem]["category"], 0]

    for filename in os.listdir(path_problems):
        for theorem in load_json(path_problems + filename)["theorem_seqs"]:
            t_name = theorem.split("(", 1)[0]
            t_msg[t_name][1] += 1

    parsed_theorem_GDL = GDLParser.parse_theorem_gdl(
        load_json(path_gdl + "theorem_GDL.json"),
        GDLParser.parse_predicate_gdl(load_json(path_gdl + "predicate_GDL.json"))
    )

    p2t_map = {}
    for t_name in t_msg:
        if t_msg[t_name][1] == 0 or t_msg[t_name][0] == 3:  # skip no used and diff t
            continue
        for t_branch in parsed_theorem_GDL[t_name]["body"]:
            theorem_unit = parsed_theorem_GDL[t_name]["body"][t_branch]
            premises = list(theorem_unit["products"])
            premises += list(theorem_unit["logic_constraints"])
            premises += list(theorem_unit["attr_in_algebra_constraints"])
            for predicate, p_vars in premises:
                if predicate[0] == "~":  # skip oppose
                    continue
                if predicate not in p2t_map:
                    p2t_map[predicate] = [(t_name, t_branch, p_vars)]
                elif (t_name, t_branch, p_vars) not in p2t_map[predicate]:
                    p2t_map[predicate].append((t_name, t_branch, p_vars))

    save_json(p2t_map, path_search_log + "p2t_map.json")
    return p2t_map


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
    warnings.filterwarnings("ignore")
    if direction == "fw":
        searcher = ForwardSearcher(
            load_json(path_gdl + "predicate_GDL.json"),
            load_json(path_gdl + "theorem_GDL.json"),
            method="bfs", max_depth=5, beam_size=5,
            p2t_map=get_p2t_map())
    else:
        # searcher = BackwardSearcher(
        #     load_json(path_gdl + "predicate_GDL.json"),
        #     load_json(path_gdl + "theorem_GDL.json"),
        #     max_depth=15, strategy=method)
        searcher = ForwardSearcher(
            load_json(path_gdl + "predicate_GDL.json"),
            load_json(path_gdl + "theorem_GDL.json"),
            method="bfs", max_depth=5, beam_size=5,
            p2t_map=get_p2t_map())

    while True:
        if task_queue.empty():
            break
        problem_id = task_queue.get()
        timing = time.time()
        try:
            searcher.init_search(load_json(path_problems + "{}.json".format(problem_id)))
            solved, seqs = searcher.search()
        except BaseException as e:
            reply_queue.put((current_process(), problem_id, "error", repr(e), time.time() - timing, 0))
        else:
            if solved:
                reply_queue.put((current_process(), problem_id, "solved", seqs, time.time() - timing, 0))
            else:
                reply_queue.put((current_process(), problem_id, "unsolved", "None", time.time() - timing, 0))


def auto(direction, method):
    """Auto run search on all problems."""
    filename = "{}-{}.json".format(direction, method)
    log = load_json(path_search_log + filename)
    data = load_json(path_search_data + filename)
    pool = []  # save process_id

    task_queue = Queue()
    reply_queue = Queue()

    for problem_id in range(log["start_pid"], log["end_pid"] + 1):  # assign tasks
        if problem_id in log["solved_pid"] or problem_id in log["unsolved_pid"] or problem_id in log["error_pid"]:
            continue
        task_queue.put(problem_id)

    print("process_id\tproblem_id\tresult\tmsg")
    while True:  # run process and
        start_process(direction, method, pool, task_queue, reply_queue)
        if len(pool) == 0:  # no unhandled problem
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
            method="bfs", max_depth=5, beam_size=5
        )
        pass
    else:
        pass


if __name__ == '__main__':
    # run(direction="fw", method="dfs")
    auto(direction="fw", method="dfs")
