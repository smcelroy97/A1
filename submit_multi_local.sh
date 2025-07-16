EXP_NAME="single_i_ou_subnet/single_i_ou_subnet_conn_wmult_0.05_pyr_pv_ikdr_multi"

PARS=(
  "IT2 0"
  "ITP4 0"
)

source ~/.bashrc
conda activate netpyne_batch
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
export MKL_THREADING_LAYER=GNU

cd /ddn/niknovikov19/repo/A1_OUinp

for PAR in "${PARS[@]}"; do
  echo "Param: $PAR"
  mpiexec nrniv -python -mpi run_exp.py --name "$EXP_NAME" --par "$PAR"
done

#mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi run_exp.py --name "$EXP_NAME"
#mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi run_exp_sub.py --name "$EXP_NAME"





