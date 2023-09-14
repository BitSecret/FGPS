import random


def split(start_pid, end_pid, seed, ratio):
    """train:validation:test = 6:2:2"""
    total = ratio[0] + ratio[1] + ratio[2]
    random.seed(seed)
    data = list(range(start_pid, end_pid + 1))
    train_set = sorted(random.sample(data, int(end_pid * ratio[0] / total)))
    for i in range(len(data))[::-1]:
        if data[i] in train_set:
            data.pop(i)
    validation_set = sorted(random.sample(data, int(end_pid * ratio[1] / total)))
    for i in range(len(data))[::-1]:
        if data[i] in validation_set:
            data.pop(i)
    test_set = data
    return train_set, validation_set, test_set


if __name__ == '__main__':
    train, val, test = split(start_pid=1, end_pid=6981, seed=619, ratio=(6, 2, 2))
    print("train({}/6981): {}".format(len(train), train))
    print("val({}/6981): {}".format(len(val), val))
    print("test({}/6981): {}".format(len(test), test))
