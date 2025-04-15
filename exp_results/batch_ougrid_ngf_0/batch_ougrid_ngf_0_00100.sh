#!/bin/bash
#$ -N jobbatch_ougrid_ngf_0_00100
#$ -q cpu.q
#$ -pe smp 30
#$ -l h_vmem=128G
#$ -l h_rt=2:00:00
#$ -o /ddn/smcelroy97/A1-OUinp/exp_results/batch_ougrid_ngf_0/batch_ougrid_ngf_0_00100.run
cd /ddn/smcelroy97/A1-OUinp
source ~/.bashrc
export JOBID=$JOB_ID
export SOCNAME="('10.0.0.16', 37901)"

export TUPLERUNTK0="ou_tuple=(-0.0253448275862068, 0.0103448275862068)"
export STRRUNTK1="saveFolder=./exp_results/batch_ougrid_ngf_0"
export STRRUNTK2="simLabel=batch_ougrid_ngf_0_00100"
conda activate netpyne_sm 
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH 
export MKL_THREADING_LAYER=GNU 
mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi run_exp.py --batch
