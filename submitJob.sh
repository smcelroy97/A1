#!/bin/bash
#$ -cwd
#$ -N OUGrid
#$ -q cpu.q
#$ -pe smp 8
#$ -l h_vmem=64G
#$ -V
#$ -l h_rt=12:00:00
#$ -o /ddn/smcelroy97/A1-OUinp/batch.out
#$ -e /ddn/smcelroy97/A1-OUinp/batch.err

source ~/.bashrc
conda activate netpyne_sm
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
cd /ddn/smcelroy97/A1-OUinp
python grid_search.py