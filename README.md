# FGPS

[![Version](https://img.shields.io/badge/Version-1.0-brightgreen)](https://github.com/BitSecret/FGPS)
[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)
[![Survey](https://img.shields.io/badge/Survey-FormalGeo-blue)](https://github.com/FormalGeo/FormalGeo)  
Formal geometric problem solver (FGPS) based on FormalGeo.

This project utilizes [FormalGeo](https://github.com/FormalGeo/FormalGeo) as its problem solver and conduct experiments
on datasets [formalgeo7k](https://github.com/FormalGeo/Datasets/tree/main/projects/formalgeo7k) and
[formalgeo-imo](https://github.com/FormalGeo/Datasets/tree/main/projects/formalgeo-imo). Our paper introducing the
functions and implementation of FGPS can be obtained at [Symmetry 2024](https://www.mdpi.com/2073-8994/16/4/404).

More information about FormalGeo will be found in [homepage](https://formalgeo.github.io/). FormalGeo is in its early
stages and brimming with potential. We welcome anyone to join us in this exciting endeavor.

## Installation

You can get the source by cloning the FGPS repository.   
Create Python environment:

	$ conda create -n FGPS python=3.10
	$ conda activate FGPS

Clone project:

    $ git clone --depth 1 https://github.com/BitSecret/FGPS.git

Install python dependencies:

    $ cd FGPS
    $ pip install -e .

## Run

Enter the path:

    $ cd src/fgps

Download datasets _formalgeo7k_v1_ and _formalgeo-imo_v1_:

    $ python utils.py --func download_datasets --path_datasets ./user_datasets

Create logs dir:

    $ python utils.py --func create_log_archi --path_logs ./user_logs

View help information for personalizing configuration:

    $ python utils.py --help

### Auto problem-solving based on search

Check our search results on _formalgeo7k_v1_ dataset:

    $ python check_search.py --func check_search --path_datasets ./user_datasets

Run the search method on your own computer:

    $ python search.py --path_datasets ./user_datasets --path_logs ./user_logs --dataset_name formalgeo7k_v1 --method fw --strategy bfs 

### Interactive problem-solving

Check our results:

    $ python check_run.py --func check_run --path_datasets ./user_datasets

Verify the annotated problems in the dataset:

    $ python run.py --func auto_run --path_datasets ./user_datasets --path_logs ./user_logs --dataset_name formalgeo7k_v1
    $ python run.py --func auto_run --path_datasets ./user_datasets --path_logs ./user_logs --dataset_name formalgeo-imo_v1

Run interactively and show detail solution:

    $ python run.py --func run --path_datasets ./user_datasets --path_logs ./user_logs --dataset_name formalgeo7k_v1
    $ python run.py --func run --path_datasets ./user_datasets --path_logs ./user_logs --dataset_name formalgeo-imo_v1

You can find detail solution output in `./user_logs/run/problems`.

### Others

Draw fig.8 and fig.9:

    $ python check_run.py --func draw_run_results --path_datasets ./user_datasets
    $ python check_search.py --func draw_search_results --path_datasets ./user_datasets

The image will be saved to `./231016/run/auto_logs`.

## Results

We conducted experiments on the formalgeo7k_v1, comparing different search methods and strategies in terms of
problem-solving success rate, solution time, and the number of steps required for problem-solving.  
Forward search (FW) starts from the known conditions of the problem and continuously apply theorems to derive new
conditions until the goal is achieved. Backward search (BW), on the other hand, begins with the problem-solving goal,
expands it into multiple sub-goals, and repeats this process until all sub-goals are resolved.  
The search-based methods construct a search tree during the problem-solving process. We have the flexibility to choose
various strategies to traverse the search tree and reach the goal. Breadth-first search (BFS) begins by expanding the
top-level nodes of the search tree and then proceeds layer by layer into the depth. Depth-first search (DFS) recursively
selects nodes from the search tree from shallow to deep and continues this process. Random search (RS) randomly selects
an expandable node at each stage of expansion. Beam search (BS) selects $k$ nodes in each stage of expansion and can be
viewed as a trade-off between BFS and RS.  
We conducted experiments on 2 Intel i9-10900X, 1 AMD Ryzen 9 5900X, and 1 AMD Ryzen 9 7950X, running the search
algorithms using multiple processes while maintaining a CPU utilization rate of 80\%. The maximum search depth was set
to 15, and the beam size was set to 20. The total duration of the experiments was approximately 3 days. When the timeout
for each problem was 300 seconds, the best success rate for problem-solving was approximately 30\%. When the timeout for
each problem was increased to 600 seconds, the specific results are as follows.

**The number of problems for different levels.**

| total | l1   | l2   | l3   | l4  | l5  | l6  |
|-------|------|------|------|-----|-----|-----|
| 6981  | 2409 | 1896 | 1248 | 824 | 313 | 291 |

**Results of search-based problem-solving success rates**

| method | strategy | solved | unsolved | timeout |
|--------|----------|--------|----------|---------|
| FW     | BFS      | 38.86  | 7.42     | 53.72   |
| FW     | DFS      | 36.16  | 9.80     | 54.05   |
| FW     | RS       | 39.71  | 9.07     | 51.22   |
| FW     | BS       | 25.28  | 38.72    | 36.00   |
| BW     | BFS      | 35.44  | 2.68     | 61.88   |
| BW     | DFS      | 33.73  | 2.42     | 63.84   |
| BW     | RS       | 34.05  | 2.65     | 63.30   |
| BW     | BS       | 34.39  | 12.86    | 52.74   |

**Detail results of search-based problem-solving success rates**

| method | strategy | total | l1    | l2    | l3    | l4    | l5   | l6   |
|--------|----------|-------|-------|-------|-------|-------|------|------|
| FW     | BFS      | 38.86 | 59.94 | 38.61 | 28.53 | 17.35 | 8.63 | 3.78 |
| FW     | DFS      | 36.16 | 55.75 | 40.03 | 22.92 | 12.38 | 7.03 | 4.12 |
| FW     | RS       | 39.71 | 59.24 | 40.03 | 33.65 | 16.38 | 5.43 | 4.81 |
| FW     | BS       | 25.28 | 46.12 | 22.57 | 13.46 | 5.83  | 2.88 | 0.34 |
| BW     | BFS      | 35.44 | 67.21 | 33.70 | 11.14 | 6.67  | 6.07 | 1.03 |
| BW     | DFS      | 33.73 | 65.88 | 30.85 | 8.89  | 6.55  | 5.11 | 0.69 |
| BW     | RS       | 34.05 | 66.58 | 31.70 | 8.65  | 5.83  | 4.47 | 0.69 |
| BW     | BS       | 34.39 | 67.08 | 31.33 | 9.46  | 6.31  | 5.75 | 1.03 |

**Timing (solved)**

| method | strategy | total  | l1     | l2     | l3     | l4     | l5     | l6     |
|--------|----------|--------|--------|--------|--------|--------|--------|--------|
| FW     | BFS      | 185.05 | 121.92 | 205.74 | 333.33 | 331.26 | 243.92 | 251.11 |
| FW     | DFS      | 132.35 | 84.07  | 159.07 | 254.29 | 196.02 | 230.39 | 218.05 |
| FW     | RS       | 92.21  | 57.34  | 89.67  | 177.34 | 189.74 | 166.96 | 199.31 |
| FW     | BS       | 58.76  | 35.09  | 81.66  | 106.97 | 207.55 | 191.40 | 121.36 |
| BW     | BFS      | 57.67  | 30.28  | 94.34  | 152.26 | 147.55 | 193.21 | 134.65 |
| BW     | DFS      | 46.45  | 26.34  | 81.17  | 115.83 | 94.85  | 133.23 | 0.85   |
| BW     | RS       | 65.82  | 42.79  | 101.71 | 156.27 | 145.50 | 202.37 | 3.37   |
| BW     | BS       | 75.55  | 47.44  | 120.53 | 172.50 | 165.80 | 207.28 | 146.26 |

**Timing (unsolved)**

| method | strategy | total  | l1     | l2     | l3     | l4     | l5     | l6     |
|--------|----------|--------|--------|--------|--------|--------|--------|--------|
| FW     | BFS      | 574.94 | 434.92 | 584.16 | 615.29 | 624.06 | 663.15 | 681.07 |
| FW     | DFS      | 548.81 | 418.40 | 546.35 | 594.46 | 605.72 | 641.69 | 655.53 |
| FW     | RS       | 542.46 | 394.11 | 546.29 | 591.92 | 606.37 | 632.35 | 649.81 |
| FW     | BS       | 355.74 | 277.04 | 345.92 | 358.74 | 429.92 | 446.75 | 452.67 |
| BW     | BFS      | 579.24 | 549.32 | 572.41 | 592.66 | 588.48 | 596.18 | 597.48 |
| BW     | DFS      | 581.50 | 550.26 | 577.09 | 593.69 | 592.71 | 595.34 | 598.38 |
| BW     | RS       | 580.74 | 554.28 | 578.62 | 589.06 | 588.93 | 592.29 | 597.23 |
| BW     | BS       | 513.86 | 338.82 | 508.33 | 566.67 | 574.09 | 585.96 | 578.35 |

**Step size (solved)**

| method | strategy | total | l1    | l2    | l3     | l4     | l5     | l6     |
|--------|----------|-------|-------|-------|--------|--------|--------|--------|
| FW     | BFS      | 58.44 | 21.86 | 68.71 | 119.56 | 144.80 | 161.44 | 822.18 |
| FW     | DFS      | 87.16 | 33.17 | 95.99 | 225.57 | 232.25 | 257.59 | 727.17 |
| FW     | RS       | 41.89 | 19.14 | 47.66 | 64.32  | 108.26 | 143.41 | 611.00 |
| FW     | BS       | 18.64 | 11.01 | 25.95 | 37.86  | 46.19  | 48.44  | 541.00 |
| BW     | BFS      | 15.14 | 20.66 | 4.81  | 5.60   | 2.31   | 1.00   | 1.00   |
| BW     | DFS      | 5.17  | 4.96  | 5.83  | 5.86   | 3.94   | 1.00   | 1.00   |
| BW     | RS       | 4.34  | 5.02  | 3.13  | 2.81   | 1.27   | 1.00   | 1.00   |
| BW     | BS       | 1.67  | 1.49  | 1.95  | 3.08   | 1.25   | 1.00   | 1.00   |

**Step size (unsolved)**

| method | strategy | total  | l1      | l2     | l3     | l4     | l5     | l6     |
|--------|----------|--------|---------|--------|--------|--------|--------|--------|
| FW     | BFS      | 63.65  | 45.63   | 61.78  | 76.31  | 77.91  | 56.86  | 65.50  |
| FW     | DFS      | 154.25 | 89.50   | 148.21 | 154.27 | 152.39 | 204.89 | 378.16 |
| FW     | RS       | 66.38  | 65.17   | 68.91  | 75.37  | 56.14  | 62.68  | 62.81  |
| FW     | BS       | 37.44  | 27.70   | 36.13  | 41.83  | 42.55  | 40.06  | 54.81  |
| BW     | BFS      | 266.77 | 1147.53 | 195.47 | 21.51  | 10.16  | 4.49   | 59.40  |
| BW     | DFS      | 517.90 | 2649.89 | 154.48 | 6.99   | 2.18   | 1.62   | 17.26  |
| BW     | RS       | 181.74 | 828.78  | 113.62 | 15.26  | 2.14   | 1.34   | 10.19  |
| BW     | BS       | 7.17   | 22.14   | 6.81   | 3.02   | 2.48   | 1.73   | 2.01   |

## Acknowledge

This project is maintained by
[FormalGeo Development Team](https://formalgeo.github.io/)
and Supported by
[Geometric Cognitive Reasoning Group of Shanghai University (GCRG, SHU)](https://euclidesprobationem.github.io/).  
Please contact with the author (xiaokaizhang1999@163.com) if you encounter any issues.

## Citation

A BibTeX entry for LaTeX users is:
> @article{zhang2024fgeosss,  
> AUTHOR = {Zhang, Xiaokai and Zhu, Na and He, Yiming and Zou, Jia and Qin, Cheng and Li, Yang and Leng, Tuo},  
> TITLE = {FGeo-SSS: A Search-Based Symbolic Solver for Human-like Automated Geometric Reasoning},  
> JOURNAL = {Symmetry},  
> VOLUME = {16},  
> YEAR = {2024},  
> NUMBER = {4},  
> ARTICLE-NUMBER = {404},  
> URL = {https://www.mdpi.com/2073-8994/16/4/404},  
> ISSN = {2073-8994},  
> DOI = {10.3390/sym16040404}  
> }
