# FGPS

[![Version](https://img.shields.io/badge/Version-1.0-brightgreen)](https://github.com/BitSecret/FGPS)
[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)
[![Survey](https://img.shields.io/badge/Survey-FormalGeo-blue)](https://github.com/BitSecret/FGPS)  
Formal geometric problem solver based on FormalGeo.  
This project is based on the [Geometry Formalization Theory](https://arxiv.org/abs/2310.18021) and
utilizes [FormalGeo](https://github.com/BitSecret/FormalGeo) as its problem solver.

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

Check our search results on formalgeo7k-v1:

    $ python src/static.py --file_path 231016

## Results

## Related Project

## Acknowledge

This project is developed and maintained
by [Geometric Cognitive Reasoning Group of Shanghai University (GCRG, SHU)](https://euclidesprobationem.github.io/).   
**FormalGeo** is an extended version of **[GeoMechanical](https://github.com/BitSecret/GeoMechanical)**. It supports
solving more types of plane geometric problems.  
Some original problems come from the following dataset, which
are: [Geometry3K](https://github.com/lupantech/InterGPS), [GeoQA](https://github.com/chen-judge/GeoQA), [GeometryQA](https://github.com/doublebite/Sequence-to-General-tree/), [GeoQA+](https://github.com/SCNU203/GeoQA-Plus), [UniGeo](https://github.com/chen-judge/UniGeo).  
Thank you for participating in the dataset annotation. They are: [XiaokaiZhang](https://github.com/BitSecret)(
11.4%), [NaZhu](https://github.com/RuRuo0)(10.8%), [YimingHe](https://github.com/748978460)(
10.5%), [JiaZou](https://github.com/PersonNoName)(10.4%), [QikeHuang](https://github.com/huangqaqqk)(
6.9%), [XiaoxiaoJin](https://github.com/J1372628520)(6.6%), [YanjunGuo](https://github.com/g826796047)(
6.4%), [ChenyangMao](https://github.com/shadymcy)(6.3%), [ZheZhu](https://github.com/zz863474396)(
6.0%), [DengfengYue](https://github.com/331368068)(5.9%), [FangzhenZhu](https://github.com/pigsquare)(
3.9%), [YangLi](https://github.com/leeyoung628)(3.8%), [YifanWang](https://github.com/yf0216)(
3.2%), [YiwenHuang](https://github.com/Eaven21)(2.7%), [RunanWang](https://github.com/RunanW)(
2.6%), [ChengQin](https://github.com/https://github.com/Vench115)(2.5%).   
Please contact with the author (xiaokaizhang1999@163.com) if you encounter any issues.

## Citation
