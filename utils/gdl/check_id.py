import os
from solver.aux_tools.utils import load_json, save_json, load_text, save_text

gdl_pic_path = "../../doc/gdl-pic/"
max_number = 200


def get_ids_can_use():
    p_can_use = []
    t_can_use = []
    files = os.listdir(gdl_pic_path)
    for i in range(1, max_number):
        if i < 10:
            filename = "00{}".format(i)
        elif i < 100:
            filename = "0{}".format(i)
        else:
            filename = "{}".format(i)

        if "P" + filename + ".png" not in files:
            p_can_use.append(filename)

        if "T" + filename + ".png" not in files:
            t_can_use.append(filename)

    print("Predicate (can use): {}".format(p_can_use))
    print("Theorem (can use): {}".format(t_can_use))


def get_ids_can_delete():
    used = ["P001.png", "P002.png", "P003.png", "P004.png", "P005.png", "P006.png", "P007.png", "P008.png",
            "P009.png"]
    can_delete = []
    data = load_json("predicate.json")["Predicates"]
    for predicate in data["Entity"]:
        used.append(data["Entity"][predicate]["pic_name"] + ".png")
    for predicate in data["Relation"]:
        used.append(data["Relation"][predicate]["pic_name"] + ".png")
    for predicate in data["Attribution"]:
        used.append(data["Attribution"][predicate]["pic_name"] + ".png")

    data = load_json("theorem.json")["Theorems"]
    for theorem in data:
        used.append(data[theorem]["pic_name"] + ".png")

    for filename in os.listdir(gdl_pic_path):
        if filename not in used:
            can_delete.append(filename.split(".")[0])

    print("can delete): {}".format(can_delete))


if __name__ == '__main__':
    get_ids_can_use()
    get_ids_can_delete()
