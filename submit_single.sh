#!/bin/bash
#$ -cwd
#$ -N OUGrid
#$ -q cpu.q
#$ -pe smp 60
#$ -l h_vmem=256G
#$ -V
#$ -l h_rt=12:00:00
#$ -o <USER_REPO_DIR>/single.out
#$ -e <USER_REPO_DIR>/single.err

source ~/.bashrc
conda activate "<USER_CONDA_ENV>"
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
export MKL_THREADING_LAYER=GNU \n
cd "<USER_REPO_DIR>"
mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi run_exp.py --name "<EXP_NAME>"
