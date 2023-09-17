from solver.aux_tools.utils import load_json
from utils.augment.get_data_aug import assemble
path_problems = "../../datasets/problems/"
path_problems_augment = "../../datasets/problems-augment/"


def statistic_predicate(augment=False):
    predicate_used = {}
    goal_used = {"Relation": 0, "Value": 0}

    for pid in range(1, 6982):
        problem_CDL = load_json(path_problems + "{}.json".format(pid))
        predicates = problem_CDL["construction_cdl"] + problem_CDL["text_cdl"] + problem_CDL["image_cdl"]
        for predicate in predicates:
            predicate = predicate.split("(")[0]
            if predicate not in predicate_used:
                predicate_used[predicate] = 0
            predicate_used[predicate] += 1

        if "Value" in problem_CDL["goal_cdl"]:
            goal_used["Value"] += 1
        else:
            goal_used["Relation"] += 1

        if augment:
            augment_data = load_json(path_problems_augment + "{}.json".format(pid))
            for ag_pid in augment_data:
                augment_CDL = assemble(problem_CDL, augment_data[ag_pid])
                predicates = augment_CDL["construction_cdl"] + augment_CDL["text_cdl"] + augment_CDL["image_cdl"]
                for predicate in predicates:
                    predicate = predicate.split("(")[0]
                    if predicate not in predicate_used:
                        predicate_used[predicate] = 0
                    predicate_used[predicate] += 1

                if "Value" in augment_CDL["goal_cdl"]:
                    goal_used["Value"] += 1
                else:
                    goal_used["Relation"] += 1

        print("problem {} ok.".format(pid))

    print("predicate_used: {}".format(predicate_used))
    print("goal_used: {}".format(goal_used))

    print()
    predicate_used = sorted(predicate_used.items(), key=lambda x: x[1], reverse=True)
    print("predicate\tused_count")
    for predicate, count in predicate_used:
        print("{}\t{}".format(predicate, count))

    print()
    goal_used = sorted(goal_used.items(), key=lambda x: x[1], reverse=True)
    print("goal\tused_count")
    for goal, count in goal_used:
        print("{}\t{}".format(goal, count))


def statistic_theorem(augment=False):
    t_len = {}
    t_used = {}

    for pid in range(1, 6982):
        theorem_seqs = load_json(path_problems + "{}.json".format(pid))["theorem_seqs"]
        if len(theorem_seqs) not in t_len:
            t_len[len(theorem_seqs)] = 0
        t_len[len(theorem_seqs)] += 1
        for theorem in theorem_seqs:
            t_name = theorem.split("(")[0]
            if t_name not in t_used:
                t_used[t_name] = 0
            t_used[t_name] += 1

        if augment:
            augment_data = load_json(path_problems_augment + "{}.json".format(pid))
            for ag_pid in augment_data:
                theorem_seqs = augment_data[ag_pid]["theorem_seqs"]
                if len(theorem_seqs) not in t_len:
                    t_len[len(theorem_seqs)] = 0
                t_len[len(theorem_seqs)] += 1
                for theorem in theorem_seqs:
                    t_used[theorem.split("(")[0]] += 1

        print("problem {} ok.".format(pid))

    print()
    t_len = sorted(t_len.items(), key=lambda x: x[0], reverse=False)
    print("len(seqs)\tproblem_count")
    for length, count in t_len:
        print("{}\t{}".format(length, count))

    print()
    t_used = sorted(t_used.items(), key=lambda x: x[1], reverse=True)
    print("t_name\tused_count")
    for t_name, count in t_used:
        print("{}\t{}".format(t_name, count))


if __name__ == '__main__':
    statistic_predicate(augment=True)
    # statistic_theorem(augment=True)
