#!/bin/bash
#$ -cwd
#$ -N SMgridSearch
#$ -q cpu.q
#$ -pe smp 30
#$ -l h_vmem=128G
#$ -l h_rt=1:40:00
#$ -o /ddn/smcelroy97/A1model_sm/data/singleSim.out
#$ -e /ddn/smcelroy97/A1model_sm/data/singleSim.err

source ~/.bashrc
mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py