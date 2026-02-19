#!/bin/bash
#SBATCH --job-name=outer-grid
#SBATCH -A TG-MED240050
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=4G
#SBATCH --time=48:00:00
#SBATCH --output=outer_%j.out
#SBATCH --error=outer_%j.err

module purge
module load cpu
module load slurm

cd /path/to/project
python outer_grid.py