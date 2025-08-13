#!/bin/bash
#$ -cwd
#$ -N SMgridSearch
#$ -q cpu.q
#$ -pe smp 6
#$ -l h_vmem=64G
#$ -l h_rt=2:40:00
#$ -o //ddn/smcelroy97/A1/batch.out
#$ -e /ddn/smcelroy97/A1/batch.err

source ~/.bashrc
python batch.py