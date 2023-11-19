import os
from formalgeo.data import download_dataset
import argparse

parser = argparse.ArgumentParser(description="Welcome to use FGPS!")
parser.add_argument("--datasets_path", type=str, required=True, help="datasets path")
datasets_path = parser.parse_args().datasets_path
if not os.path.exists(datasets_path):
    os.makedirs(datasets_path)

download_dataset("formalgeo7k_v1", datasets_path)
download_dataset("formalgeo-imo_v1", datasets_path)
