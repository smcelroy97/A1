from netpyne.batchtools.search import search
import numpy as np

label = 'sgeTest0909'

params = {'intraThalamicIEGain' : np.linspace(0.4),
          'intraThalamicEIGain' : np.linspace(0.5)
          }

# use batch_shell_config if running directly on the machine
shell_config = {'command': 'mpiexec -np 4 nrniv -python -mpi init.py',}

# use batch_sge_config if running on Downstate HPC or other SGE systems
sge_config = {
    'queue': 'cpu.q',
    'cores': 64,
    'vmem': '256G',
    'walltime': '00:20:00',
    'command': 'mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py'}

run_config = sge_config

search(job_type = 'sge',
       comm_type = 'socket',
       label = label,
       params = params,
       output_path = str('../A1/simOutput/' + label + '/'),
       checkpoint_path = '../A1/simOutput/ray',
       run_config = run_config,
       num_samples = 1,
       metric = 'loss',
       mode = 'min',
       algorithm = "variant_generator",
       max_concurrent = 9)
