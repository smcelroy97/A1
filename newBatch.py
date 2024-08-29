from netpyne.batchtools.search import search
import numpy as np

params = {'cochlearThalInput.weightECore' : 0.5}#np.linspace(0.3, 0.9, 4)}

# use batch_shell_config if running directly on the machine
shell_config = {'command': 'mpiexec -np 4 nrniv -python -mpi init.py',}

# use batch_sge_config if running on Downstate HPC or other SGE systems
sge_config = {
    'queue': 'cpu.q',
    'cores': 64,
    'vmem': '256G',
    'realtime': '00:20:00',
    'command': 'mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py'}

run_config = shell_config

search(job_type = 'sh',
       comm_type = 'socket',
       label = 'grid',
       params = params,
       output_path = '../A1m/data/grid_batch',
       checkpoint_path = '../A1/data/ray',
       run_config = run_config,
       num_samples = 1,
       metric = 'loss',
       mode = 'min',
       algorithm = "variant_generator",
       max_concurrent = 9)
