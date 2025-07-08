#!/bin/bash
#$ -cwd
#$ -N OUPost
#$ -q cpu.q
#$ -pe smp 6
#$ -l h_vmem=128G
#$ -V
#$ -l h_rt=12:00:00
#$ -o /ddn/niknovikov19/repo/A1_OUinp/post.out
#$ -e /ddn/niknovikov19/repo/A1_OUinp/post.err

source ~/.bashrc
conda activate netpyne_batch
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
#cd /ddn/niknovikov19/repo/A1_OUinp/exp_configs/batch_i_ou/batch_i_ou_rx_switch_var_oumean_mech_v
cd /ddn/niknovikov19/repo/A1_OUinp/exp_configs/batch_i_ou_subnet/batch_i_ou_subnet_wmult_0.05_pyr_ikdr_mult_3s_6pts
python post_batch.py
