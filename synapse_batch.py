from netpyne.batchtools.search import search
import numpy as np

label = 'v45_batch29'

params = {'prePop': ['NGF1', 'IT2', 'SOM2', 'PV2', 'VIP2', 'NGF2', 'IT3', 'SOM3', 'PV3', 'VIP3', 'NGF3', 'ITP4', 'ITS4',
                     'SOM4', 'PV4', 'VIP4', 'NGF4', 'IT5A', 'CT5A', 'SOM5A', 'PV5A', 'VIP5A', 'NGF5A', 'IT5B', 'PT5B', 'CT5B',
                     'SOM5B', 'PV5B', 'VIP5B', 'NGF5B', 'IT6', 'CT6', 'SOM6', 'PV6', 'VIP6', 'NGF6']}


# use batch_shell_config if running directly on the machine
shell_config = {'command': 'mpiexec -np 4 nrniv -python -mpi init.py'}

# use batch_sge_config if running on Downstate HPC or other SGE systems
sge_config = {
    'queue': 'cpu.q',
    'cores': 24,
    'vmem': '128G',
    'realtime': '02:40:00',
    'command': 'mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi synapse_init.py'
}

slurm_config = {
    'allocation': 'TG-MED240050',
    'walltime': '5:40:00',
    'partition': 'compute',
    'nodes': 1,
    'coresPerNode': 64,
    'mem' : 128,
    'email': 'scott.mcelroy@downstate.edu',
    'command': 'mpiexec -n 64 nrniv -python -mpi synapse_init.py'
}

run_config = sge_config
search(job_type='sge',
       comm_type='sfs',
       label=label,
       params=params,
       output_path=str('../A1/simOutput/' + label + '/'),
       checkpoint_path='../A1/simOutput/ray',
       run_config=run_config,
       num_samples=1,
       metric='loss',
       mode='min',
       algorithm="variant_generator",
       max_concurrent=10)
