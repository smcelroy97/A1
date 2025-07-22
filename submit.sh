#!/bin/bash
#$ -cwd
#$ -N SMgridSearch
#$ -q cpu.q
#$ -pe smp 45
#$ -l h_vmem=256G
#$ -l h_rt=2:40:00
#$ -o /ddn/smcelroy97/A1/singleSim.out
#$ -e /ddn/smcelroy97/A1/singleSim.err

source ~/.bashrc
mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py