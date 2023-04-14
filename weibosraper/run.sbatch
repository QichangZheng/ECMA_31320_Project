#!/bin/bash

#SBATCH --job-name=Q1a
#SBATCH --output=Q1a.out
#SBATCH --ntasks=1
#SBATCH --partition=broadwl
#SBATCH --constraint=fdr
#SBATCH --account=macs30123

module load python/anaconda-2019.03
module load intelmpi/2018.2.199+intel-18.0

mpirun -n 1 python3 Q1a.py > Q1a.out