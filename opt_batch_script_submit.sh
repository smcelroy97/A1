#!/bin/bash
#$ -cwd
#$ -N BATCH_MAIN
#$ -q cpu.q
#$ -pe smp 8
#$ -l h_vmem=64G
#$ -V
#$ -l h_rt=12:00:00
#$ -o /ddn/niknovikov19/repo/A1_OUinp/exp_results/sim_manager_batch/exp_subnet_state1_mech1_nosub_wmult_0.25/its4_pt5b/log/batch_script_log.out
#$ -e /ddn/niknovikov19/repo/A1_OUinp/exp_results/sim_manager_batch/exp_subnet_state1_mech1_nosub_wmult_0.25/its4_pt5b/log/batch_script_log.err

source ~/.bashrc
conda activate netpyne_batch
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
cd /ddn/niknovikov19/repo/A1_OUinp
python opt_batch_script.py "/ddn/niknovikov19/repo/A1_OUinp/exp_results/sim_manager_batch/exp_subnet_state1_mech1_nosub_wmult_0.25/its4_pt5b" "sim_manager_batch/exp_subnet_state1_mech1_nosub_wmult_0.25"