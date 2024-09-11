"""
batch.py

Batch simulation for M1 model using NetPyNE

Contributors: salvadordura@gmail.com
"""
from netpyne.batch import Batch
from netpyne import specs
import numpy as np


# ----------------------------------------------------------------------------------------------
# 40 Hz ASSR optimization
# ----------------------------------------------------------------------------------------------

def assr_batch_grid(filename):
    params = specs.ODict()

    #### SET weights####
    params['intraThalamicIEGain'] = [0.1]
    params['intraThalamicEIGain'] = [0.3]

    # --------------------------------------------------------

    # grouped params
    groupedParams = []

    # initial config
    initCfg = {}


    b = Batch(params=params, netParamsFile='netParams.py', cfgFile='cfg.py', initCfg=initCfg,
              groupedParams=groupedParams)
    b.method = 'grid'

    return b

# ----------------------------------------------------------------------------------------------
# Run configurations
# ----------------------------------------------------------------------------------------------

def setRunCfg(b, type='hpc_sge'):
    if type == 'hpc_sge':
        b.runCfg = {'type': 'hpc_sge',  # for downstate HPC
                    'jobName': 'smc_ASSR_batch',  # label for job
                    'cores': 64,  # give 60 cores here
                    'script': 'init.py',  # what you normally run
                    'vmem': '256G',  # or however much memory you need
                    'walltime': '2:15:00',  # make 2 hours or something
                    'skip': True}
    elif type == 'hpc_slurm_Expanse':
        b.runCfg = {'type': 'hpc_slurm',
                    'allocation': 'TG-IBN140002',
                    'partition': 'compute',
                    'walltime': '1:40:00',
                    'nodes': 1,
                    'coresPerNode': 64,
                    'folder': '/home/smcelroy/A1/',
                    'script': 'init.py',
                    'mpiCommand': 'mpirun',
                    'custom': '#SBATCH --constraint="lustre"\n#SBATCH --export=ALL\n#SBATCH --partition=compute',
                    'skip': True,
                    'skipCustom': '_data.pkl'}

    elif type == 'hpc_slurm_JUSUF':
        b.runCfg = {'type': 'hpc_slurm',
                    'allocation': 'icei-hbp-00000000006',
                    'walltime': '0:40:00',
                    'nodes': 1,
                    'coresPerNode': 128,
                    'folder': '/p/home/jusers/mcelroy1/jusuf/A1',
                    'script': 'init.py',
                    'mpiCommand': 'srun',
                    'skip': True,
                    'skipCustom': '_data.pkl'}

    elif type == 'mpi_direct':
        b.runCfg = {'type': 'mpi_direct',
                    'cores': 1,
                    'script': 'init.py',
                    'mpiCommand': 'mpirun',  # --use-hwthread-cpus
                    'skip': True}
    # ------------------------------


# ----------------------------------------------------------------------------------------------
# Main code
# ----------------------------------------------------------------------------------------------

if __name__ == '__main__':
    b = assr_batch_grid('data/v34_batch25/trial_2142/trial_2142_cfg.json')

    b.batchLabel = 'netTest0910'
    b.saveFolder = 'data/' + b.batchLabel

    setRunCfg(b, 'hpc_slurm_Expanse')
    b.run()  # run batch
