from netpyne.batchtools.search import search
import numpy as np

label = 'v45_batch28'

# params for search
params = {
    'addSubConn': [1]
}


# use batch_shell_config if running directly on the machine
shell_config = {'command': 'mpiexec -np 6 nrniv -python -mpi init.py'}

# use batch_sge_config if running on Downstate HPC or other SGE systems
sge_config = {
    'queue': 'cpu.q',
    'cores': 20,
    'vmem': '64G',
    'realtime': '02:00:00',
    'command': 'mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py'
}

slurm_config = {
    'allocation' : 'TG-IBN140002',
    'walltime' : '0:40:00',
    'nodes' : 1,
    'coresPerNode' : 64,
    'email' : 'scott.mcelroy@downstate.edu',
    'command' : 'mpiexec -n 128 nrniv -python -mpi init.py'
}



run_config = sge_config
search(job_type = 'sge',
       comm_type = 'sfs',
       label = label,
       params = params,
       output_path = str('../A1/simOutput/' + label + '/'),
       checkpoint_path = '../A1/simOutput/ray',
       run_config = run_config,
       num_samples = 1,
       metric = 'loss',
       mode = 'min',
       algorithm = "variant_generator",
       max_concurrent= 10)