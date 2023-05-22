#!/bin/bash

#SBATCH --job-name=crawler
#SBATCH --output=crawler.out
#SBATCH --ntasks=20
#SBATCH --partition=broadwl
#SBATCH --constraint=fdr
#SBATCH --account=macs30123

#module load python/anaconda-2021.05
#module load intelmpi/2018.2.199+intel-18.0

#for i in {2..4}
#do
#    mpirun -n 2 python3 run_spider.py $i &
#    pid=$!
#    wait $pid
#done

for d in {0..0}
do
    for i in {0..4}
    do
        mpirun -n 2 python3 run_spider.py 2022-05-09 $d $i &
        pid=$!
        wait $pid
    done
done