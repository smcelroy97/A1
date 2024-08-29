#!/bin/bash
#----------------------------------------------------
# Slurm job script
#   for TACC Stampede2 SKX nodes
#
#----------------------------------------------------

#SBATCH -J NoCxThal0617         # Job name
#SBATCH -o NoCxThal0617.o%j       # Name of stdout output file
#SBATCH -e NoCxThal0617.e%j       # Name of stderr error file
#SBATCH -A TG-IBN140002			# Project ID (this is our current account)
#SBATCH -p skx-dev                      # Queue (partition) name
#SBATCH -N 4               # Total # of nodes (must be 1 for serial)
#SBATCH -n 192               # Total # of mpi tasks (should be 1 for serial)
#SBATCH -t 00:40:00        # Run time (hh:mm:ss)
#SBATCH --mail-user=[YOUR EMAIL ADDRESS]
#SBATCH --mail-type=all    # Send email at begin and end of job
ibrun --npernode=48 nrniv -python -mpi init.py
