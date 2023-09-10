import os
from solver.aux_tools.utils import save_json

search_data_path = "../../datasets/search/"
direction = ["fw", "bw"]  # forward, backward
method = ["dfs", "bfs", "rs", "bs"]  # deep first, breadth first, random, beam
data = {"start_pid": 1, "end_pid": 6981, "solved_pid": [], "unsolved_pid": [], "error_pid": []}


def init_search():
    for d in direction:
        for m in method:
            filename = "{}-{}.json".format(d, m)
            if filename not in os.listdir():
                save_json(data, filename)
                save_json({}, search_data_path + filename)


if __name__ == '__main__':
    init_search()
