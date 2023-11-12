# FGPS

[![Version](https://img.shields.io/badge/Version-1.0-brightgreen)](https://github.com/BitSecret/FGPS)
[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)
[![Survey](https://img.shields.io/badge/Survey-FormalGeo-blue)](https://github.com/FormalGeo/FormalGeo)  
Formal geometric problem solver based on FormalGeo.  
This project is based on the [Geometry Formalization Theory](https://arxiv.org/abs/2310.18021) and
utilizes [FormalGeo](https://github.com/FormalGeo/FormalGeo) as its problem solver.

## Installation

You can get the source by cloning the FGPS repository.   
Create Python environment:

	$ conda create -n FGPS python=3.10
	$ conda activate FGPS

Clone project:

    $ git clone https://github.com/BitSecret/FGPS.git

Install python dependencies:

    $ cd FGPS
    $ pip install -e .

## Run

Enter the path where the code is located:

    $ cd src/fgps/search

Check our search results on formalgeo7k-v1 dataset:

    $ python check.py --dataset formalgeo7k-v1 --file_path 231016

Run the search method on your own computer:

    $ python search.py --dataset formalgeo7k-v1 --direction fw --method bfs --file_path my_search

View help information for personalizing configuration of search methods:

    $ python search.py --help

## Results

## Acknowledge

This project is maintained by
[Geometric Cognitive Reasoning Group of Shanghai University (GCRG, SHU)](https://euclidesprobationem.github.io/)
and Supported by
[Geometric Cognitive Reasoning Group of Shanghai University (GCRG, SHU)](https://euclidesprobationem.github.io/).  
Please contact with the author (xiaokaizhang1999@163.com) if you encounter any issues.

## Citation

A BibTeX entry for LaTeX users is:
> @misc{arxiv2023formalgeo,  
> title={FormalGeo: The First Step Toward Human-like IMO-level Geometric Automated Reasoning},  
> author={Xiaokai Zhang and Na Zhu and Yiming He and Jia Zou and Qike Huang and Xiaoxiao Jin and Yanjun Guo and Chenyang
> Mao and Zhe Zhu and Dengfeng Yue and Fangzhen Zhu and Yang Li and Yifan Wang and Yiwen Huang and Runan Wang and Cheng
> Qin and Zhenbing Zeng and Shaorong Xie and Xiangfeng Luo and Tuo Leng},  
> year={2023},  
> eprint={2310.18021},  
> archivePrefix={arXiv},  
> primaryClass={cs.AI}  
> }
