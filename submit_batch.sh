#!/bin/bash
#$ -cwd
#$ -N OUGrid
#$ -q cpu.q
#$ -pe smp 8
#$ -l h_vmem=64G
#$ -V
#$ -l h_rt=12:00:00
#$ -o /ddn/niknovikov19/repo/A1_OUinp/batch.out
#$ -e /ddn/niknovikov19/repo/A1_OUinp/batch.err

source ~/.bashrc
conda activate netpyne_batch
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
cd /ddn/niknovikov19/repo/A1_OUinp
python grid_search.py