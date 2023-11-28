import os
from formalgeo.data import download_dataset
import psutil
import argparse

method = ["fw", "bw"]  # forward, backward
strategy = ["bfs", "dfs", "rs", "bs"]  # deep first, breadth first, random, beam


def get_args():
    parser = argparse.ArgumentParser(description="Welcome to use FGPS!")

    # func
    parser.add_argument("--func", type=str, required=False, default="",
                        help="function that you want to run")

    # file path
    parser.add_argument("--path_datasets", type=str, required=False, default="./user_datasets",
                        help="datasets path")
    parser.add_argument("--path_logs", type=str, required=False, default="./user_logs",
                        help="path that save search log and result")

    # basic search para
    parser.add_argument("--dataset_name", type=str, required=False, default="formalgeo7k_v1",
                        help="dataset name")
    parser.add_argument("--method", type=str, required=False, choices=("fw", "bw"), default="fw",
                        help="search method")
    parser.add_argument("--strategy", type=str, required=False, choices=("bfs", "dfs", "rs", "bs"), default="bfs",
                        help="search strategy")

    # other search para
    parser.add_argument("--max_depth", type=int, required=False, default=15,
                        help="max search depth")
    parser.add_argument("--beam_size", type=int, required=False, default=20,
                        help="search beam size")
    parser.add_argument("--timeout", type=int, required=False, default=300,
                        help="search timeout")
    parser.add_argument("--process_count", type=int, required=False, default=int(psutil.cpu_count() * 0.8),
                        help="multi process count")
    parser.add_argument("--random_seed", type=int, required=False, default=619,
                        help="random seed")

    return parser.parse_args()


def create_log_archi(path_logs):
    filepaths = [
        os.path.join(path_logs, "search"),
        os.path.join(path_logs, "run/auto_logs"),
        os.path.join(path_logs, "run/problems")
    ]

    for filepath in filepaths:
        if not os.path.exists(filepath):
            os.makedirs(filepath)


def download_datasets(path_datasets):
    if not os.path.exists(path_datasets):
        os.makedirs(path_datasets)

    download_dataset("formalgeo7k_v1", path_datasets)
    download_dataset("formalgeo-imo_v1", path_datasets)


if __name__ == '__main__':
    args = get_args()

    if args.func == "download_datasets":
        download_datasets(args.path_datasets)
    elif args.func == "create_log_archi":
        create_log_archi(args.path_logs)
    else:
        msg = "No function name {}.".format(args.func)
        raise Exception(msg)
