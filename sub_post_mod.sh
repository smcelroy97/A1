#!/bin/bash
#SBATCH --job-name=outer-grid
#SBATCH -A TG-IBN140002
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=50G
#SBATCH --time=04:00:00
#SBATCH --output=post_run.out
#SBATCH --error=post_run.err

module purge
module load cpu
module load slurm
source .bashrc
conda activate fitune

python post_run_mod.py