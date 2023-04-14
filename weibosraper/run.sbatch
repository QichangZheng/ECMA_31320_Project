#!/bin/bash

#SBATCH --job-name=crawler
#SBATCH --output=crawler.out
#SBATCH --ntasks=121
#SBATCH --nodes=100
#SBATCH --partition=broadwl
#SBATCH --constraint=fdr
#SBATCH --account=macs30123

module load python/anaconda-2021.05
module load intelmpi/2018.2.199+intel-18.0

mpirun -n 121 python3 run_spider.py