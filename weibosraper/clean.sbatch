#!/bin/bash

#SBATCH --job-name=clean
#SBATCH --output=clean.out
#SBATCH --ntasks=20
#SBATCH --partition=broadwl
#SBATCH --constraint=fdr
#SBATCH --account=macs30123

#module load python/anaconda-2021.05
#module load intelmpi/2018.2.199+intel-18.0

mpirun -n 3 python3 clean.py 2022-05-08