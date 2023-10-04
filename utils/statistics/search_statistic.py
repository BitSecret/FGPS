from utils.search.init_search import direction, method
from solver.aux_tools.utils import load_json

path_problems = "../../datasets/problems/"
path_search_data = "../../datasets/solved/search/"
path_search_log = "../search/"


def main():
    print("roughly")
    print("direction\tmethod\tsolved\tunsolved\ttimeout\terror\tunhandled")
    for d in direction:
        for m in method:
            data = load_json(path_search_log + "{}-{}.json".format(d, m))
            total = 6981
            solved = len(data["solved_pid"])
            unsolved = len(data["unsolved_pid"])
            timeout = len(data["timeout_pid"])
            error = len(data["error_pid"])
            unhandled = total - (solved + unsolved + timeout + error)
            print("{}\t{}\t{}/{}\t{}/{}\t{}/{}\t{}/{}\t{}/{}".format(
                d, m,
                solved, total,
                unsolved, total,
                timeout, total,
                error, total,
                unhandled, total))
    print()

    print("roughly (percent)")
    print("direction\tmethod\tsolved\tunsolved\ttimeout\terror\tunhandled")
    for d in direction:
        for m in method:
            data = load_json(path_search_log + "{}-{}.json".format(d, m))
            total = 6981
            solved = len(data["solved_pid"])
            unsolved = len(data["unsolved_pid"])
            timeout = len(data["timeout_pid"])
            error = len(data["error_pid"])
            unhandled = total - (solved + unsolved + timeout + error)
            print("{}\t{}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}".format(
                d, m,
                solved / total * 100,
                unsolved / total * 100,
                timeout / total * 100,
                error / total * 100,
                unhandled / total * 100))
    print()

    j_map = {}  # map pid to column
    i_map = {}  # map config tp row

    count = 0
    for d in direction:
        for m in method:
            i_map[(d, m)] = count
            count += 1

    for pid in range(1, 6982):
        problem_CDL = load_json(path_problems + "{}.json".format(pid))
        t_length = len(problem_CDL["theorem_seqs"])
        if t_length <= 3:
            j_map[pid] = 1
        elif t_length <= 6:
            j_map[pid] = 2
        elif t_length <= 9:
            j_map[pid] = 3
        elif t_length <= 12:
            j_map[pid] = 4
        elif t_length <= 15:
            j_map[pid] = 5
        else:
            j_map[pid] = 6

    solving = [[[0 for _ in range(2)] for _ in range(7)] for _ in range(8)]  # [count(S), count(U)]
    timing = [[[0 for _ in range(2)] for _ in range(7)] for _ in range(8)]  # [item(S), item(U)]
    step_size = [[[0 for _ in range(2)] for _ in range(7)] for _ in range(8)]  # [item(S), item(U)]

    for d in direction:
        for m in method:
            search_data = load_json(path_search_data + "{}-{}.json".format(d, m))
            search_data["unsolved"].update(search_data["timeout"])
            search_data["unsolved"].update(search_data["error"])
            i = i_map[(d, m)]

            for pid in range(1, 6982):
                j = j_map[pid]
                if str(pid) in search_data["solved"]:
                    k = 0
                elif str(pid) in search_data["unsolved"]:
                    k = 1
                else:
                    continue
                problem_data = search_data["solved"][str(pid)] if k == 0 else search_data["unsolved"][str(pid)]

                solving[i][j][k] += 1
                timing[i][j][k] += problem_data["timing"]
                step_size[i][j][k] += problem_data["step_size"]

    for d in direction:
        for m in method:
            i = i_map[(d, m)]
            for j in range(1, 7):
                solving[i][0][0] += solving[i][j][0]
                timing[i][0][0] += timing[i][j][0]
                step_size[i][0][0] += step_size[i][j][0]
                solving[i][0][1] += solving[i][j][1]
                timing[i][0][1] += timing[i][j][1]
                step_size[i][0][1] += step_size[i][j][1]

    print("solving")
    print("direction\tmethod\t"
          "total(S)\ttotal(U)\t"
          "l<=3(S)\tl<=3(U)\t"
          "4<=l<=6(S)\t4<=l<=6(U)\t"
          "7<=l<=9(S)\t7<=l<=9(U)\t"
          "10<=l<=12(S)\t10<=l<=12(U)\t"
          "13<=l<=15(S)\t13<=l<=15(U)\t"
          "l>=16(S)\tl>=16(U)")
    for d in direction:
        for m in method:
            print("{}\t{}\t".format(d, m), end="")
            i = i_map[(d, m)]
            for j in range(7):
                total = solving[i][j][0] + solving[i][j][1]
                print("{}/{}\t{}/{}\t".format(solving[i][j][0], total, solving[i][j][1], total), end="")
            print()
    print()

    print("solving (percent)")
    print("direction\tmethod\t"
          "total(S)\ttotal(U)\t"
          "l<=3(S)\tl<=3(U)\t"
          "4<=l<=6(S)\t4<=l<=6(U)\t"
          "7<=l<=9(S)\t7<=l<=9(U)\t"
          "10<=l<=12(S)\t10<=l<=12(U)\t"
          "13<=l<=15(S)\t13<=l<=15(U)\t"
          "l>=16(S)\tl>=16(U)")
    for d in direction:
        for m in method:
            print("{}\t{}\t".format(d, m), end="")
            i = i_map[(d, m)]
            for j in range(7):
                total = solving[i][j][0] + solving[i][j][1]
                print("{:.2f}\t{:.2f}\t".format(solving[i][j][0] / total * 100,
                                                solving[i][j][1] / total * 100), end="")
            print()
    print()

    print("timing")
    print("direction\tmethod\t"
          "total(S)\ttotal(U)\t"
          "l<=3(S)\tl<=3(U)\t"
          "4<=l<=6(S)\t4<=l<=6(U)\t"
          "7<=l<=9(S)\t7<=l<=9(U)\t"
          "10<=l<=12(S)\t10<=l<=12(U)\t"
          "13<=l<=15(S)\t13<=l<=15(U)\t"
          "l>=16(S)\tl>=16(U)")
    for d in direction:
        for m in method:
            print("{}\t{}\t".format(d, m), end="")
            i = i_map[(d, m)]
            for j in range(7):
                if timing[i][j][0] == 0:
                    para1 = "NaN"
                else:
                    para1 = "{:.2f}".format(timing[i][j][0] / solving[i][j][0])

                if timing[i][j][1] == 0:
                    para2 = "NaN"
                else:
                    para2 = "{:.2f}".format(timing[i][j][1] / solving[i][j][1])
                print("{}\t{}\t".format(para1, para2), end="")
            print()
    print()

    print("step_size")
    print("direction\tmethod\t"
          "total(S)\ttotal(U)\t"
          "l<=3(S)\tl<=3(U)\t"
          "4<=l<=6(S)\t4<=l<=6(U)\t"
          "7<=l<=9(S)\t7<=l<=9(U)\t"
          "10<=l<=12(S)\t10<=l<=12(U)\t"
          "13<=l<=15(S)\t13<=l<=15(U)\t"
          "l>=16(S)\tl>=16(U)")
    for d in direction:
        for m in method:
            print("{}\t{}\t".format(d, m), end="")
            i = i_map[(d, m)]
            for j in range(7):
                if step_size[i][j][0] == 0:
                    para1 = "NaN"
                else:
                    para1 = "{:.2f}".format(step_size[i][j][0] / solving[i][j][0])

                if step_size[i][j][1] == 0:
                    para2 = "NaN"
                else:
                    para2 = "{:.2f}".format(step_size[i][j][1] / solving[i][j][1])
                print("{}\t{}\t".format(para1, para2), end="")
            print()


if __name__ == '__main__':
    main()
