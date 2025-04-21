#!/bin/bash
#$ -cwd
#$ -N OUGrid
#$ -q cpu.q
#$ -pe smp 6
#$ -l h_vmem=128G
#$ -V
#$ -l h_rt=12:00:00
#$ -o <USER_REPO_DIR>/batch.out
#$ -e <USER_REPO_DIR>/batch.err

source ~/.bashrc
conda activate "<USER_CONDA_ENV>"
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
cd "<USER_REPO_DIR>"
python grid_search.py
