#!/bin/bash
#$ -N jobbatch_ougrid_ngf_0_00815
#$ -q cpu.q
#$ -pe smp 30
#$ -l h_vmem=128G
#$ -l h_rt=2:00:00
#$ -o /ddn/smcelroy97/A1-OUinp/exp_results/batch_ougrid_ngf_0/batch_ougrid_ngf_0_00815.run
cd /ddn/smcelroy97/A1-OUinp
source ~/.bashrc
export JOBID=$JOB_ID
export SOCNAME="('10.0.0.16', 57495)"

export TUPLERUNTK0="ou_tuple=(0.0118965517241379, 0.0051724137931034)"
export STRRUNTK1="saveFolder=./exp_results/batch_ougrid_ngf_0"
export STRRUNTK2="simLabel=batch_ougrid_ngf_0_00815"
conda activate netpyne_sm 
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH 
export MKL_THREADING_LAYER=GNU 
mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi run_exp.py --batch
