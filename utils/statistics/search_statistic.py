from utils.search.init_search import direction, method
from solver.aux_tools.utils import load_json

path_problems = "../../datasets/problems/"
path_search_data = "../../datasets/solved/search/"
path_search_log = "../search/"


def main():
    config_count = 8   # search configuration count
    level_count = 6    # problem level count
    problem_total = [0 for _ in range(level_count + 1)]
    i_map = {}
    j_map = {}

    count = 0
    for d in direction:
        for m in method:
            i_map[(d, m)] = count
            count += 1
    for pid in range(1, 6982):
        problem_CDL = load_json(path_problems + "{}.json".format(pid))
        t_length = len(problem_CDL["theorem_seqs"])
        if t_length <= 2:
            j_map[pid] = 1
        elif t_length <= 4:
            j_map[pid] = 2
        elif t_length <= 6:
            j_map[pid] = 3
        elif t_length <= 8:
            j_map[pid] = 4
        elif t_length <= 10:
            j_map[pid] = 5
        else:
            j_map[pid] = 6

        problem_total[j_map[pid]] += 1

    for i in range(1, level_count + 1):
        problem_total[0] += problem_total[i]

    print("problem count\ntotal" + "".join(["\tl{}".format(i + 1) for i in range(level_count)]))
    for i in range(level_count + 1):
        print("{}\t".format(problem_total[i]), end="")

    print("\n\nroughly\nmethod\tstrategy\tsolved\tunsolved\ttimeout\terror\tunhandled")
    for d in direction:
        for m in method:
            data = load_json(path_search_log + "{}-{}.json".format(d, m))
            solved = len(data["solved_pid"])
            unsolved = len(data["unsolved_pid"])
            timeout = len(data["timeout_pid"])
            error = len(data["error_pid"])
            unhandled = problem_total[0] - (solved + unsolved + timeout + error)
            print("{}\t{}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}".format(
                d.upper(), m.upper(),
                solved / problem_total[0] * 100,
                unsolved / problem_total[0] * 100,
                timeout / problem_total[0] * 100,
                error / problem_total[0] * 100,
                unhandled / problem_total[0] * 100))

    solved_count = [[0 for _ in range(level_count + 1)] for _ in range(config_count)]
    timing_solved = [[0 for _ in range(level_count + 1)] for _ in range(config_count)]
    timing_unsolved = [[0 for _ in range(level_count + 1)] for _ in range(config_count)]
    step_size_solved = [[0 for _ in range(level_count + 1)] for _ in range(config_count)]
    step_size_unsolved = [[0 for _ in range(level_count + 1)] for _ in range(config_count)]

    for d in direction:
        for m in method:
            search_data = load_json(path_search_data + "{}-{}.json".format(d, m))
            search_data["unsolved"].update(search_data["timeout"])
            search_data["unsolved"].update(search_data["error"])
            i = i_map[(d, m)]

            for pid in range(1, 6982):
                j = j_map[pid]
                if str(pid) in search_data["solved"]:
                    problem_data = search_data["solved"][str(pid)]
                    solved_count[i][j] += 1
                    timing_solved[i][j] += problem_data["timing"]
                    step_size_solved[i][j] += problem_data["step_size"]
                elif str(pid) in search_data["unsolved"]:
                    problem_data = search_data["unsolved"][str(pid)]
                    timing_unsolved[i][j] += problem_data["timing"]
                    step_size_unsolved[i][j] += problem_data["step_size"]

    for d in direction:
        for m in method:
            i = i_map[(d, m)]
            for j in range(level_count):
                solved_count[i][0] += solved_count[i][j + 1]
                timing_solved[i][0] += timing_solved[i][j + 1]
                timing_unsolved[i][0] += timing_unsolved[i][j + 1]
                step_size_solved[i][0] += step_size_solved[i][j + 1]
                step_size_unsolved[i][0] += step_size_unsolved[i][j + 1]

    print("\nsolved\nmethod\tstrategy\ttotal" + "".join(["\tl{}".format(i + 1) for i in range(level_count)]))
    for d in direction:
        for m in method:
            print("{}\t{}".format(d, m).upper(), end="")
            i = i_map[(d, m)]
            for j in range(level_count + 1):
                print("\t{:.2f}".format(solved_count[i][j] / problem_total[j] * 100), end="")
            print()

    print("\ntiming_solved\nmethod\tstrategy\ttotal" + "".join(["\tl{}".format(i + 1) for i in range(level_count)]))
    for d in direction:
        for m in method:
            print("{}\t{}".format(d, m).upper(), end="")
            i = i_map[(d, m)]
            for j in range(level_count + 1):
                if solved_count[i][j] == 0:
                    print("\tNaN", end="")
                else:
                    timing_solved[i][j] = timing_solved[i][j] / solved_count[i][j]
                    print("\t{:.2f}".format(timing_solved[i][j]), end="")
            print()

    print("\ntiming_unsolved\nmethod\tstrategy\ttotal" + "".join(["\tl{}".format(i + 1) for i in range(level_count)]))
    for d in direction:
        for m in method:
            print("{}\t{}".format(d, m).upper(), end="")
            i = i_map[(d, m)]
            for j in range(level_count + 1):
                timing_unsolved[i][j] = timing_unsolved[i][j] / (problem_total[j] - solved_count[i][j])
                print("\t{:.2f}".format(timing_unsolved[i][j]), end="")
            print()

    print("\nstep_size_solved\nmethod\tstrategy\ttotal" + "".join(["\tl{}".format(i + 1) for i in range(level_count)]))
    for d in direction:
        for m in method:
            print("{}\t{}".format(d, m).upper(), end="")
            i = i_map[(d, m)]
            for j in range(level_count + 1):
                if solved_count[i][j] == 0:
                    print("\tNaN", end="")
                else:
                    step_size_solved[i][j] = step_size_solved[i][j] / solved_count[i][j]
                    print("\t{:.2f}".format(step_size_solved[i][j]), end="")
            print()

    print("\nstep_size_unsolved\nmethod\tstrategy\ttotal" + "".join(["\tl{}".format(i + 1) for i in range(level_count)]))
    for d in direction:
        for m in method:
            print("{}\t{}".format(d, m).upper(), end="")
            i = i_map[(d, m)]
            for j in range(level_count + 1):
                step_size_unsolved[i][j] = step_size_unsolved[i][j] / (problem_total[j] - solved_count[i][j])
                print("\t{:.2f}".format(step_size_unsolved[i][j]), end="")
            print()

    return i_map, timing_solved, timing_unsolved, step_size_solved, step_size_unsolved


if __name__ == '__main__':
    main()
