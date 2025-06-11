#!/bin/bash
#$ -cwd
#$ -N OUorg
#$ -q cpu.q
#$ -pe smp 30
#$ -l h_vmem=128G
#$ -V
#$ -l h_rt=0:30:00
#$ -o /ddn/niknovikov19/repo/A1_OUinp/org.out
#$ -e /ddn/niknovikov19/repo/A1_OUinp/org.err

source ~/.bashrc

cd ~/repo/A1_OUinp

echo "Move configs"
mkdir -p exp_configs/batch_i_ougrid
mv exp_configs/batch_i_ougrid_* exp_configs/batch_i_ougrid/
mkdir -p exp_configs/batch_g_ougrid
mv exp_configs/batch_ougrid_* exp_configs/batch_g_ougrid/
mv exp_configs/test_* exp_configs/UNUSED
mv exp_configs/batch_ouamp_all_unconn_1 exp_configs/UNUSED
mv exp_configs/batch_oumean_ngf1_unconn exp_configs/UNUSED
mkdir -p exp_configs/single_i_ou
mv exp_configs/single_i_ou_* exp_configs/single_i_ou/

echo "Move results"
mkdir -p exp_results/batch_i_ougrid
mv exp_results/batch_i_ougrid_* exp_results/batch_i_ougrid/
mkdir -p exp_results/batch_g_ougrid
mv exp_results/batch_ougrid_* exp_results/batch_g_ougrid/
mv exp_results/test_* exp_results/UNUSED
mv exp_results/batch_ouamp_all_unconn_1 exp_results/UNUSED
mv exp_results/batch_oumean_ngf1_unconn exp_results/UNUSED
mv exp_results/sim_output_old exp_results/UNUSED
mkdir -p exp_results/single_i_ou
mv exp_results/single_i_ou_* exp_results/single_i_ou/
mv exp_results/single_g_ou_subnet_* exp_results/subnet/single/

echo "Move csv files"
mkdir -p OLD/csv
mv *.csv OLD/csv