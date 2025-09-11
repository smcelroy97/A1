#!/bin/bash

#SBATCH --job-name=NewTest
#SBATCH --account=TG-IBN140002
#SBATCH --partition=gpu-shared
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --cpus-per-task=1
#SBATCH --mem=120G
#SBATCH --gpus=3
#SBATCH --time=02:00:00
#SBATCH --output=simOutput/output/test_%j.out
#SBATCH --error=simOutput/output/test_%j.err
#SBATCH --export=ALL

cd $SLURM_SUBMIT_DIR

# Conda setup
source ~/.bashrc

# Load modules
echo "Loading modules..."
module purge
module use /cm/shared/apps/spack/0.21.2/gpu/dev/share/spack/lmod/linux-rocky8-x86_64/Core
module load nvhpc/24.11/2utxz5z
module load openmpi/mlnx/gcc/64/4.1.5a1
module load cmake/3.31.2/w4akk6u

# Run simulation with special
time mpirun --bind-to none -n $SLURM_NTASKS ./x86_64/special -mpi -python init.py
