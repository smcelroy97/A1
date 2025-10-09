import numpy as np
import json
from netpyne.batchtools.search import generate_constructors
from batchtk.algos import optuna_search
from batchtk.utils import expand_path
import os

output_dir=os.path.abspath('./optimization')
os.makedirs(output_dir, exist_ok=True)

label = 'v45_optuna3'

num_samples = 200000

# with open('data/ssh_key.json', 'r') as f:
#     key = json.load(f)
#
# ssh_key = key['ssh_key']

# params for search
params = {'EELayerGain.1': [0.1, 5.0],
          'EELayerGain.2': [0.1, 5.0],
          'EELayerGain.3': [0.1, 5.0],
          'EELayerGain.4': [0.1, 5.0],
          'EELayerGain.5A': [0.1, 5.0],
          'EELayerGain.5B': [0.1, 5.0],
          'EELayerGain.6': [0.1, 5.0],
          'EILayerGain.1': [0.1, 5.0],
          'EILayerGain.2': [0.1, 5.0],
          'EILayerGain.3': [0.1, 5.0],
          'EILayerGain.4': [0.1, 5.0],
          'EILayerGain.5A': [0.1, 5.0],
          'EILayerGain.5B': [0.1, 5.0],
          'EILayerGain.6': [0.1, 5.0],
          'IELayerGain.1': [0.1, 5.0],
          'IELayerGain.2': [0.1, 5.0],
          'IELayerGain.3': [0.1, 5.0],
          'IELayerGain.4': [0.1, 5.0],
          'IELayerGain.5A': [0.1, 5.0],
          'IELayerGain.5B': [0.1, 5.0],
          'IELayerGain.6': [0.1, 5.0],
          'IILayerGain.1': [0.1, 5.0],
          'IILayerGain.2': [0.1, 5.0],
          'IILayerGain.3': [0.1, 5.0],
          'IILayerGain.4': [0.1, 5.0],
          'IILayerGain.5A': [0.1, 5.0],
          'IILayerGain.5B': [0.1, 5.0],
          'IILayerGain.6': [0.1, 5.0]
          }




CONFIG_EXPANSE_CPU = """
source ~/.bashrc
module purge
module load shared
module load cpu/0.17.3b  gcc/10.2.0/npcyll4 openmpi/4.1.1/ygduf2r
module load sdsc
module load cpu
"""

CONFIG_EXPANSE_GPU = """
echo "Loading modules..."
source ~/.bashrc
module purge
module use /cm/shared/apps/spack/0.21.2/gpu/dev/share/spack/lmod/linux-rocky8-x86_64/Core
module load nvhpc/24.11/2utxz5z
module load openmpi/mlnx/gcc/64/4.1.5a1
module load cmake/3.31.2/w4akk6u
"""

dispatcher, submit = generate_constructors('slurm', 'sfs')
slurm_config: {'''
        'allocation': 'TG-MED240050',
        'realtime': '2:40:00',
        'partition': 'compute',
        'nodes': 1,
        'coresPerNode': 64,
        'mem': '200G',
        'custom': '',
        'email': 'scott.mcelroy@downstate.edu',
        'command': f"""
        {CONFIG_EXPANSE_CPU}
        mpirun -n $SLURM_NTASKS nrniv -python -mpi init.py
        '''
    }

results = optuna_search(
    study_label=label,
    param_space=params,
    metrics={'loss': 'minimize'},  #
    num_trials=num_trials, num_workers=6,
    dispatcher_constructor = dispatcher,
    submit_constructor = submit,
    submit_kwargs= slurm_config,
    interval=15,
    project_path='.',
    output_path=output_dir,
    )  # host alias (can use ssh tunneling through config file)


results.to_csv('./optimization/search_results.csv')