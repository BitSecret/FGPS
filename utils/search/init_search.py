import os
from solver.aux_tools.utils import load_json, save_json
from solver.aux_tools.parser import GDLParser

direction = ["fw", "bw"]  # forward, backward
method = ["dfs", "bfs", "rs", "bs"]  # deep first, breadth first, random, beam
data = {"solved": [], "unsolved": [], "timeout": [], "error": []}
log = {"start_pid": 1, "end_pid": 6981, "solved_pid": [], "unsolved_pid": [], "timeout_pid": [], "error_pid": []}


path_gdl = "../../datasets/gdl/"
path_problems = "../../datasets/problems/"
path_search_data = "../../datasets/search/"
path_raw_gdl = "../gdl/"


def init_search(force=False):
    for d in direction:
        for m in method:
            filename = "{}-{}.json".format(d, m)
            if force:
                save_json(log, filename)
                save_json(data, path_search_data + filename)
            elif filename not in os.listdir():
                save_json(log, filename)
                save_json(data, path_search_data + filename)


def init_p2t_map():
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

    p2t_map_fw = {}
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
                if predicate not in p2t_map_fw:
                    p2t_map_fw[predicate] = [(t_name, t_branch, p_vars)]
                elif (t_name, t_branch, p_vars) not in p2t_map_fw[predicate]:
                    p2t_map_fw[predicate].append((t_name, t_branch, p_vars))
    save_json(p2t_map_fw, "p2t_map-fw.json")

    p2t_map_bw = {}
    for t_name in parsed_theorem_GDL:
        if t_name in t_msg and (t_msg[t_name][1] == 0 or t_msg[t_name][0] == 3):  # skip no used and diff t
            continue

        for branch in parsed_theorem_GDL[t_name]["body"]:
            theorem_unit = parsed_theorem_GDL[t_name]["body"][branch]
            conclusions = list(theorem_unit["conclusions"])
            conclusions += list(theorem_unit["attr_in_conclusions"])
            for predicate, _ in conclusions:
                if predicate == "Equal":
                    continue
                if predicate not in p2t_map_bw:
                    p2t_map_bw[predicate] = [(t_name, branch)]
                elif (t_name, branch) not in p2t_map_bw[predicate]:
                    p2t_map_bw[predicate].append((t_name, branch))
    save_json(p2t_map_bw, "p2t_map-bw.json")


if __name__ == '__main__':
    # init_search()
    init_p2t_map()
