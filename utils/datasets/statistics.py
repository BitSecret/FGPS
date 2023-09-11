import os
from solver.aux_tools.utils import load_json, save_json
path_gdl = "../gdl/"
path_problems = "../../datasets/problems/"
path_search_log = "../search/"


def get_t_msg():
    """
    :return result: <dict>, {t_name: (category, using_count)}
    category = 1, simple theorem. category = 2, complex theorem.
    category = 3, super complex theorem. category = 4, special theorem.
    """
    result = {}
    gdl = load_json(path_gdl + "theorem.json")["Theorems"]
    for theorem in gdl:
        t_name = theorem.split("(", 1)[0]
        result[t_name] = [gdl[theorem]["category"], 0]

    for filename in os.listdir(path_problems):
        for theorem in load_json(path_problems + filename)["theorem_seqs"]:
            t_name = theorem.split("(", 1)[0]
            result[t_name][1] += 1
    print("{")
    for t_name in result:
        print("'{}':{},".format(t_name, result[t_name]))
    print("}")


if __name__ == '__main__':
    get_t_msg()
