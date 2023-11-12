import matplotlib.pyplot as plt
from fgps import check
from fgps import method


def draw_diff():
    diff_data_7k = [
        [1, 1064, 15.24136943],
        [2, 1343, 19.23793153],
        [3, 975, 13.96648045],
        [4, 923, 13.22160149],
        [5, 701, 10.04154133],
        [6, 546, 7.82122905],
        [7, 495, 7.090674688],
        [8, 329, 4.712791864],
        [9, 184, 2.635725541],
        [10, 129, 1.847872798],
        [11, 88, 1.260564389],
        [12, 50, 0.716229767],
        [13, 43, 0.615957599],
        [14, 32, 0.458387051],
        [15, 18, 0.257842716],
        [16, 21, 0.300816502],
        [17, 13, 0.186219739],
        [18, 6, 0.085947572],
        [19, 7, 0.100272167],
        [20, 7, 0.100272167],
        [21, 3, 0.042973786],
        [22, 1, 0.014324595],
        [23, 1, 0.014324595],
        [24, 1, 0.014324595],
        [28, 1, 0.014324595]
    ]
    diff_data_186k = [
        (1, 59802, 32.00843539),
        (2, 36976, 19.79104222),
        (3, 25466, 13.63042734),
        (4, 18388, 9.841997088),
        (5, 13293, 7.114948189),
        (6, 9669, 5.175237647),
        (7, 6693, 3.582362764),
        (8, 4657, 2.492613685),
        (9, 3048, 1.631412178),
        (10, 2100, 1.124004453),
        (11, 1647, 0.881540635),
        (12, 1121, 0.600004282),
        (13, 1029, 0.550762182),
        (14, 815, 0.436220776),
        (15, 629, 0.336666096),
        (16, 488, 0.261197225),
        (17, 353, 0.188939796),
        (18, 144, 0.077074591),
        (19, 172, 0.092061317),
        (20, 70, 0.037466815),
        (21, 80, 0.042819217),
        (22, 127, 0.067975507),
        (23, 25, 0.013381005),
        (24, 12, 0.006422883),
        (25, 5, 0.002676201),
        (26, 7, 0.003746682),
        (27, 6, 0.003211441),
        (28, 10, 0.005352402)
    ]

    timing_data_7k = [
        [1, 47.76031637, 1064, 44.88751539],
        [2, 52.00352407, 1343, 38.72190921],
        [3, 49.87401867, 975, 51.15283966],
        [4, 56.77583838, 923, 61.51228426],
        [5, 56.63652205, 701, 80.79389737],
        [6, 86.35611987, 546, 158.1613917],
        [7, 71.57484365, 495, 144.5956437],
        [8, 50.87618899, 329, 154.6388723],
        [9, 35.8487649, 184, 194.830244],
        [10, 23.89150095, 129, 185.2054337],
        [11, 22.12203836, 88, 251.3867996],
        [12, 13.68907189, 50, 273.7814379],
        [13, 14.95777225, 43, 347.8551687],
        [14, 21.375669, 32, 667.9896563],
        [15, 3.973545074, 18, 220.7525041],
        [16, 10.69665813, 21, 509.3646731],
        [17, 10.59225655, 13, 814.7889651],
        [18, 1.176323414, 6, 196.0539023],
        [19, 4.576915979, 7, 653.8451399],
        [20, 6.559111118, 7, 937.015874],
        [21, 0.725077629, 3, 241.692543],
        [22, 0.337882757, 1, 337.8827572],
        [23, 0.198913097, 1, 198.9130974],
        [24, 0.349102974, 1, 349.1029739],
        [28, 0.781722784, 1, 781.722784]
    ]
    timing_data_186k = [
        [1, 3662.047204, 59802, 61.23619953],
        [2, 3017.554721, 36976, 81.60846823],
        [3, 2672.088114, 25466, 104.9276727],
        [4, 2390.789017, 18388, 130.0189807],
        [5, 2168.36061, 13293, 163.1204852],
        [6, 1999.705542, 9669, 206.8161694],
        [7, 1815.154053, 6693, 271.2018606],
        [8, 1551.985427, 4657, 333.2586273],
        [9, 1321.825761, 3048, 433.669869],
        [10, 1012.366436, 2100, 482.0792555],
        [11, 1101.70562, 1647, 668.9165879],
        [12, 919.3497193, 1121, 820.1157175],
        [13, 1017.03672, 1029, 988.3738771],
        [14, 566.5106468, 815, 695.1050881],
        [15, 544.6919274, 629, 865.9649085],
        [16, 471.1091988, 488, 965.3877025],
        [17, 366.7147489, 353, 1038.85198],
        [18, 121.2964602, 144, 842.3365288],
        [19, 148.710928, 172, 864.5984184],
        [20, 88.7903738, 70, 1268.433911],
        [21, 108.4914749, 80, 1356.143436],
        [22, 196.7863204, 127, 1549.498586],
        [23, 44.430094, 25, 1777.20376],
        [24, 21.39318395, 12, 1782.765329],
        [25, 6.944256067, 5, 1388.851213],
        [26, 12.14687276, 7, 1735.267537],
        [27, 9.715337038, 6, 1619.22284],
        [28, 12.11903644, 10, 1211.903644]
    ]

    diff_lengths_7k = [row[0] for row in diff_data_7k]
    diff_percentages_7k = [row[2] for row in diff_data_7k]
    diff_lengths_186k = [row[0] for row in diff_data_186k]
    diff_percentages_186k = [row[2] for row in diff_data_186k]

    timing_lengths_7k = [row[0] for row in timing_data_7k]
    timing_avg_7k = [row[3] for row in timing_data_7k]
    timing_lengths_186k = [row[0] for row in timing_data_186k]
    timing_avg_186k = [row[3] for row in timing_data_186k]

    fig = plt.figure(figsize=(14, 4))
    fontsize = 14

    plt.subplot(141)
    plt.plot(diff_lengths_7k, diff_percentages_7k, label='FormalGeo7k')
    plt.xlabel("Difficulty", fontsize=fontsize)
    plt.ylabel("Frequency (%)", fontsize=fontsize)
    plt.title(" ", fontsize=fontsize)
    plt.legend()

    plt.subplot(142)
    plt.plot(diff_lengths_186k, diff_percentages_186k, label='FormalGeo186k', color='orange')
    plt.xlabel("Difficulty", fontsize=fontsize)
    plt.ylabel("Frequency (%)", fontsize=fontsize)
    plt.title(" ", fontsize=fontsize)
    plt.legend()

    plt.subplot(143)
    plt.plot(timing_lengths_7k, timing_avg_7k, label='FormalGeo7k')
    plt.xlabel("Difficulty", fontsize=fontsize)
    plt.ylabel("Average Time (ms)", fontsize=fontsize)
    plt.title(" ", fontsize=fontsize)
    plt.legend()

    plt.subplot(144)
    plt.plot(timing_lengths_186k, timing_avg_186k, color='orange', label='FormalGeo186k')
    plt.xlabel("Difficulty", fontsize=fontsize)
    plt.ylabel("Average Time (ms)", fontsize=fontsize)
    plt.title(" ", fontsize=fontsize)
    plt.legend()

    fig.text(0.27, 0.94, "Distribution of problem difficulty", ha='center', fontsize=fontsize)
    fig.text(0.75, 0.94, "Average Time of Interactive verification", ha='center', fontsize=fontsize)
    plt.tight_layout()

    plt.savefig('chart_problem_level.pdf', format='pdf')
    plt.show()


def draw_solved_results():
    i_map, timing_solved, timing_unsolved, step_size_solved, step_size_unsolved = check("formalgeo7k-v1", "231016")
    x = [1, 2, 3, 4, 5, 6]

    plt.figure(figsize=(16, 8))
    fontsize = 14

    plt.subplot(241)
    for m in method:
        y = timing_solved[i_map[("fw", m)]][1:]
        plt.plot(x, y, label="{}-{}".format("fw", m).upper())
    plt.title("Time (forward, solved)", fontsize=fontsize)
    plt.xlabel("Problem Difficulty", fontsize=fontsize)
    plt.ylabel("Average time (s)", fontsize=fontsize)
    plt.legend(loc="upper left")

    plt.subplot(242)
    for m in method:
        y = timing_unsolved[i_map[("fw", m)]][1:]
        plt.plot(x, y, label="{}-{}".format("fw", m).upper())
    plt.title("Time (forward, unsolved)", fontsize=fontsize)
    plt.xlabel("Problem Difficulty", fontsize=fontsize)
    plt.ylabel("Average time (s)", fontsize=fontsize)
    plt.legend(loc="upper left")

    plt.subplot(243)
    for m in method:
        y = timing_solved[i_map[("bw", m)]][1:]
        plt.plot(x, y, label="{}-{}".format("bw", m).upper())
    plt.title("Time (backward, solved)", fontsize=fontsize)
    plt.xlabel("Problem Difficulty", fontsize=fontsize)
    plt.ylabel("Average time (s)", fontsize=fontsize)
    plt.legend(loc="upper left")

    plt.subplot(244)
    for m in method:
        y = timing_unsolved[i_map[("bw", m)]][1:]
        plt.plot(x, y, label="{}-{}".format("bw", m).upper())
    plt.title("Time (backward, unsolved)", fontsize=fontsize)
    plt.xlabel("Problem Difficulty", fontsize=fontsize)
    plt.ylabel("Average time (s)", fontsize=fontsize)
    plt.legend(loc="upper left")

    plt.subplot(245)
    for m in method:
        y = step_size_solved[i_map[("fw", m)]][1:]
        plt.plot(x, y, label="{}-{}".format("fw", m).upper())
    plt.title("Step (forward, solved)", fontsize=fontsize)
    plt.xlabel("Problem Difficulty", fontsize=fontsize)
    plt.ylabel("Average step", fontsize=fontsize)
    plt.legend(loc="upper left")

    plt.subplot(246)
    for m in method:
        y = step_size_unsolved[i_map[("fw", m)]][1:]
        plt.plot(x, y, label="{}-{}".format("fw", m).upper())
    plt.title("Step (forward, unsolved)", fontsize=fontsize)
    plt.xlabel("Problem Difficulty", fontsize=fontsize)
    plt.ylabel("Average step", fontsize=fontsize)
    plt.legend(loc="upper left")

    plt.subplot(247)
    for m in method:
        y = step_size_solved[i_map[("bw", m)]][1:]
        plt.plot(x, y, label="{}-{}".format("bw", m).upper())
    plt.title("Step (backward, solved)", fontsize=fontsize)
    plt.xlabel("Problem Difficulty", fontsize=fontsize)
    plt.ylabel("Average step", fontsize=fontsize)
    plt.legend(loc="upper left")

    plt.subplot(248)
    for m in method:
        y = step_size_unsolved[i_map[("bw", m)]][1:]
        plt.plot(x, y, label="{}-{}".format("bw", m).upper())
    plt.title("Step (backward, unsolved)", fontsize=fontsize)
    plt.xlabel("Problem Difficulty", fontsize=fontsize)
    plt.ylabel("Average step", fontsize=fontsize)
    plt.legend(loc="upper left")

    plt.tight_layout()
    plt.savefig('chart_search_results.pdf', format='pdf')
    plt.show()


if __name__ == '__main__':
    # draw_diff()
    draw_solved_results()
