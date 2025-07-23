#!/bin/bash
#$ -cwd
#$ -N SMgridSearch
#$ -q cpu.q
#$ -pe smp 20
#$ -l h_vmem=475G
#$ -l h_rt=2:40:00
#$ -o /ddn/smcelroy97/A1/singleSim.out
#$ -e /ddn/smcelroy97/A1/singleSim.err

source ~/.bashrc
conda activate "netpyne_sm"
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
# cd "A1-OUinp"
mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py