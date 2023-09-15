import random
from solver.aux_tools.utils import save_json


def split(start_pid, end_pid, seed, ratio, save_file=False):
    """train:validation:test = ratio[0]:ratio[1]:ratio[2]"""
    total = ratio[0] + ratio[1] + ratio[2]
    random.seed(seed)
    data = list(range(start_pid, end_pid + 1))
    test = sorted(random.sample(data, int(end_pid * ratio[2] / total)))
    for i in range(len(data))[::-1]:
        if data[i] in test:
            data.pop(i)
    val = sorted(random.sample(data, int(end_pid * ratio[1] / total)))
    for i in range(len(data))[::-1]:
        if data[i] in val:
            data.pop(i)
    train = data

    total = len(train) + len(val) + len(test)
    print("train({}/{}): {}".format(len(train), total, train))
    print("val({}/{}): {}".format(len(val), total, val))
    print("test({}/{}): {}".format(len(test), total, test))

    if save_file:
        data = {
            "msg": {
                "total": total,
                "train": len(train),
                "val": len(val),
                "test": len(test)
            },
            "split": {
                "train": train,
                "val": val,
                "test": test
            }
        }
        save_json(data, "{}k.json".format(str(int(total / 1000))))


if __name__ == '__main__':
    split(start_pid=1, end_pid=6981, seed=619, ratio=(6, 2, 2), save_file=True)
    # split(start_pid=1, end_pid=186832, seed=619, ratio=(15, 2, 1), save_file=True)
