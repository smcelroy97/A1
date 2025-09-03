import json
from pathlib import Path
import time
import sys

from netpyne.batchtools.search import search

#sys.path.append('/ddn/niknovikov19/repo/model_tuner')
from model_tuner.sim_manager import SimBatchPaths


# Folder name for experiment configs (relative to this script)
DIRNAME_EXP_CONFIGS = 'exp_configs'

# Base folder for requests from SimManager server and the results
dirpath_exp_manager_base = sys.argv[1]

# Experiment name: passed to run_exp.py (via cfg.simLabel and --subdir arg)
# and used there to locate exp_cfg.py and batch_params.py in DIRNAME_EXP_CONFIGS
exp_name = sys.argv[2]

# Collection of paths used by SimManagerHPCBatch
# Root: dirpath_exp_manager_base
# Children: requests_file, results_dir, batchtools_dir, log_file
sim_batch_paths = SimBatchPaths.create_default(dirpath_exp_manager_base)

# Read sim labels from the requests json file produced by SimManager.
# Each label corresponds to a set of params and will result in one job.
with open(sim_batch_paths.requests_file, 'r') as fid:
    requests = json.load(fid)
sim_labels = list(requests.keys())

# Setup a batch over the sim labels.
# Path to the json file with requests is a constant param.
batch_params = {
    'sim_manager.sim_label': sim_labels,
    'sim_manager.requests_file': [sim_batch_paths.requests_file],
}

print('Batch params:', flush=True)
print(batch_params, flush=True)

# Split exp_name into the main name and the containing subfolder.
# Main name is passed to run_exp.py via cfg.simLabel, and
# subfolder name - via --subdir cmdline arg.
if '/' in exp_name:
    exp_subdir, exp_name_main = exp_name.rsplit('/', 1)
    subdir_str = f'--subdir {exp_subdir}'
else:
    exp_name_main = exp_name
    subdir_str = ''

sge_config = {
    'queue': 'cpu.q',
    'cores': 60,
    'vmem': '256G',
    'realtime': '0:40:00',
    'command': (
        'conda activate netpyne_batch \n'
        'export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH \n'
        'export MKL_THREADING_LAYER=GNU \n'
        f'mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi run_exp.py --batch {subdir_str}'
    )
}

search(
    job_type='sge',
    comm_type='socket',
    label=exp_name_main,
    params=batch_params,
    output_path = sim_batch_paths.results_dir,
    checkpoint_path = sim_batch_paths.batchtools_dir,
    run_config=sge_config,
    num_samples=1,
    max_concurrent=10
)
