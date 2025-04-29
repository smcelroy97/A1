#!/bin/bash
#$ -cwd
#$ -N BATCH_MAIN
#$ -q cpu.q
#$ -pe smp 8
#$ -l h_vmem=64G
#$ -V
#$ -l h_rt=12:00:00
#$ -o /ddn/niknovikov19/test/model_tuner/test_opt_A1_batch_qsub/test_2_pfr_0.4_1.0_4_wmult_0.015_alpha_0.1_tcalc_2-3/log/batch_script_log.out
#$ -e /ddn/niknovikov19/test/model_tuner/test_opt_A1_batch_qsub/test_2_pfr_0.4_1.0_4_wmult_0.015_alpha_0.1_tcalc_2-3/log/batch_script_log.err

source ~/.bashrc
conda activate netpyne_batch
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
cd /ddn/niknovikov19/repo/A1_OUinp
python opt_batch_script.py "/ddn/niknovikov19/test/model_tuner/test_opt_A1_batch_qsub/test_2_pfr_0.4_1.0_4_wmult_0.015_alpha_0.1_tcalc_2-3"