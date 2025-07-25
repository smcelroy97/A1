#!/bin/bash
#SBATCH --job-name=testrun
#SBATCH -A TG-MED240050
#SBATCH -t 2:30:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=64
#SBATCH -o simOutput/single.run
#SBATCH -e simOutput/single.err
#SBATCH --mail-user=scott.mcelroy@downstate.edu
#SBATCH --mail-type=end

#SBATCH --mem=250G
#SBATCH --export=ALL
#SBATCH --partition=shared
source ~/.bashrc
cd /home/smcelroy/expanse/A1
mpirun -n 64 nrniv -python -mpi init.py 
