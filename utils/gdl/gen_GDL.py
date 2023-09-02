from solver.aux_tools.utils import load_json, save_json, load_text, save_text
doc_path = "../../doc/"
gdl_path = "../../datasets/gdl/"


def gen_predicate_gdl():
    data = load_json("predicate.json")
    entity = {}
    for name in data["Predicates"]["Entity"]:
        entity[name] = data["Predicates"]["Entity"][name]["body"]
    relation = {}
    for name in data["Predicates"]["Relation"]:
        relation[name] = data["Predicates"]["Relation"][name]["body"]
    attr = {}
    for name in data["Predicates"]["Attribution"]:
        attr[name] = data["Predicates"]["Attribution"][name]["body"]

    predicate_gdl = {
        "Preset": {
            "FixLength": ["Point", "Line", "Arc", "Angle", "Circle", "Equation"],
            "VariableLength": ["Shape", "Collinear", "Cocircular", "Polygon"],
            "Construction": ["Shape", "Collinear", "Cocircular"],
            "BasicEntity": ["Point", "Line", "Arc", "Angle", "Polygon", "Circle"],
            "Attribution": ["Free"],
            "Algebra": ["Equal"]
        },
        "Entity": entity,
        "Relation": relation,
        "Attribution": attr
    }

    save_json(predicate_gdl, gdl_path + "predicate_GDL.json")


def gen_theorem_gdl():
    data = load_json("theorem.json")
    theorem_gdl = {}
    for name in data["Theorems"]:
        theorem_gdl[name] = data["Theorems"][name]["body"]

    save_json(theorem_gdl, gdl_path + "theorem_GDL.json")


def deal_item(title, items):
    text = "    " + title + ": "
    space = " " * len(text)
    if len(items) > 0:
        text += items[0] + "\n"
        for i in range(1, len(items)):
            text += space + items[i] + "\n"
    else:
        text += "\n"

    return text


def deal_notes(notes):
    text = "**Notes**:  \n"
    for note in notes:
        text += note + "  \n"
    text += "\n"

    return text


def gen_predicate_md():
    data = load_json("predicate.json")
    text = load_text("predicate_msg_1.md")

    text += "## C、实体\n"
    for entity in data["Predicates"]["Entity"]:
        text += "### {}\n".format(entity)
        text += "<div>\n    <img src=\"gdl-pic/{}.png\" width=\"{}%\">\n</div>\n\n".format(
            data["Predicates"]["Entity"][entity]["pic_name"], data["Predicates"]["Entity"][entity]["pic_width"])
        text += deal_item("ee_check", data["Predicates"]["Entity"][entity]["body"]["ee_check"])
        text += deal_item("multi", data["Predicates"]["Entity"][entity]["body"]["multi"])
        text += deal_item("extend", data["Predicates"]["Entity"][entity]["body"]["extend"])
        text += deal_notes(data["Predicates"]["Entity"][entity]["notes"])

    text += "## D、实体关系\n"
    for relation in data["Predicates"]["Relation"]:
        text += "### {}\n".format(relation)
        text += "<div>\n    <img src=\"gdl-pic/{}.png\"  width=\"{}%\">\n</div>\n\n".format(
            data["Predicates"]["Relation"][relation]["pic_name"], data["Predicates"]["Relation"][relation]["pic_width"])
        text += deal_item("ee_check", data["Predicates"]["Relation"][relation]["body"]["ee_check"])
        if "fv_check" in data["Predicates"]["Relation"][relation]["body"]:
            text += deal_item("fv_check", data["Predicates"]["Relation"][relation]["body"]["fv_check"])
        text += deal_item("multi", data["Predicates"]["Relation"][relation]["body"]["multi"])
        text += deal_item("extend", data["Predicates"]["Relation"][relation]["body"]["extend"])
        text += deal_notes(data["Predicates"]["Relation"][relation]["notes"])

    text += "## F、实体属性\n"
    for attr in data["Predicates"]["Attribution"]:
        text += "### {}\n".format(attr)
        text += "<div>\n    <img src=\"gdl-pic/{}.png\"  width=\"{}%\">\n</div>\n\n".format(
            data["Predicates"]["Attribution"][attr]["pic_name"], data["Predicates"]["Attribution"][attr]["pic_width"])
        text += deal_item("ee_check", data["Predicates"]["Attribution"][attr]["body"]["ee_check"])
        if "fv_check" in data["Predicates"]["Attribution"][attr]["body"]:
            text += deal_item("fv_check", data["Predicates"]["Attribution"][attr]["body"]["fv_check"])
        text += deal_item("multi", data["Predicates"]["Attribution"][attr]["body"]["multi"])
        text += "    sym: {}\n".format(data["Predicates"]["Attribution"][attr]["body"]["sym"])
        text += deal_notes(data["Predicates"]["Attribution"][attr]["notes"])

    text += load_text("predicate_msg_2.md")
    save_text(text, doc_path + "predicate.md")


def gen_theorem_md():
    data = load_json("theorem.json")
    text = "# 附录3 定理标注对照手册\n"
    for t_name in data["Theorems"]:
        text += "### {}\n".format(t_name)
        text += "<div>\n    <img src=\"gdl-pic/{}.png\" width=\"{}%\"\n</div>\n\n".format(
            data["Theorems"][t_name]["pic_name"], data["Theorems"][t_name]["pic_width"])
        if len(data["Theorems"][t_name]["body"]) > 1:
            for b in data["Theorems"][t_name]["body"]:
                text += "    # branch {}\n".format(b)
                text += "    premise: {}\n".format(data["Theorems"][t_name]["body"][b]["premise"])
                text += deal_item("conclusion", data["Theorems"][t_name]["body"][b]["conclusion"])
        else:
            text += "    premise: {}\n".format(data["Theorems"][t_name]["body"]["1"]["premise"])
            text += deal_item("conclusion", data["Theorems"][t_name]["body"]["1"]["conclusion"])
        text += deal_notes(data["Theorems"][t_name]["notes"])

    save_text(text, doc_path + "theorem.md")


def show_msg():
    p_count = 3
    data = load_json("predicate.json")
    p_count += len(data["Predicates"]["BasicEntity"])
    p_count += len(data["Predicates"]["Entity"])
    p_count += len(data["Predicates"]["Relation"])
    p_count += len(data["Predicates"]["Attribution"])
    print("predicate:{}".format(p_count))
    print("theorem:{}".format(len(load_json("theorem.json")["Theorems"])))


if __name__ == '__main__':
    gen_predicate_gdl()
    gen_theorem_gdl()
    gen_predicate_md()
    gen_theorem_md()
    show_msg()
