from netpyne.batchtools.search import search
import numpy as np

label = 'v45_batch33'

# params for search
params = {
    'EEGain': np.linspace(0.99, 1.25, 4),
    'EIGain': np.linspace(0.1, 1.63, 10)
}


# use batch_shell_config if running directly on the machine
shell_config = {'command': 'mpiexec -np 6 nrniv -python -mpi init.py'}

# use batch_sge_config if running on Downstate HPC or other SGE systems
sge_config = {
    'queue': 'cpu.q',
    'cores': 40,
    'vmem': '128G',
    'realtime': '04:00:00',
    'command': 'mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py'
}

slurm_config = {
    'allocation': 'TG-IBN140002',
    'walltime': '0:40:00',
    'partition': 'shared',
    'nodes': 1,
    'coresPerNode': 64,
    'mem': '128G',
    'email': 'scott.mcelroy@downstate.edu',
    'command': 'mpiexec -n 4 nrniv -python -mpi init.py'
}

run_config = slurm_config
search(job_type='ssh_slurm',  # ssh onto an sge based submission gateway
       comm_type='sftp',  # communication through sftp
       label='grid',
       params=params,
       remote_dir='/home/smcelroy/A1',  # path to your remote directory here (make sure everything is compiled in that directory)
       output_path='/home/smcelroy/A1/simOutput/' + label,  # this will also be created as a remote directory
       checkpoint_path='/tmp/ray/grid',  # local checkpointing directory here
       run_config=run_config,
       metric='loss',  # if a metric and mode is specified, the search will collect metric data and report on the optimal configuration
       mode='min',  # currently remote submissions only support projects where session data (sim.send) is implemented
       algorithm="grid",
       max_concurrent=5,
       host='grid0')  # host alias (can use ssh tunneling through config file)
