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

#SBATCH --mem=126G
#SBATCH --export=ALL
#SBATCH --partition=compute
source ~/.bashrc
cd /home/smcelroy/expanse/A1
mpirun -n 64 nrniv -python -mpi init.py simConfig=data/ANsynapseReduction1113A/ANsynapseReduction1113A_0_0_0_cfg.json netParams=data/ANsynapseReduction1113A/ANsynapseReduction1113A_netParams.py
