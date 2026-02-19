#!/bin/bash
#SBATCH --job-name=outer-grid
#SBATCH -A TG-MED240050
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=20
#SBATCH --mem=50G
#SBATCH --time=2:00:00

module purge
module load cpu
module load slurm

cd /path/to/project
