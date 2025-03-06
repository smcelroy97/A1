#!/bin/bash
#$ -cwd
#$ -N genMap
#$ -q cpu.q
#$ -pe smp 60
#$ -l h_vmem=494G
#$ -l h_rt=1:40:00
#$ -o /ddn/smcelroy97/A1/OUmap.out
#$ -e /ddn/smcelroy97/A1/OUmap.err

source ~/.bashrc
mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi analysis/makeOUmap.py