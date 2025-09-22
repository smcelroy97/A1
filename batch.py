from netpyne.batchtools.search import search
import numpy as np
import json

label = 'v45_batch34'
num_samples = 200

with open('data/ssh_key.json', 'r') as f:
    key = json.load(f)

ssh_key = key['ssh_key']

# params for search
params = {'EELayerGain.1': 2.095792127636887,
          'EELayerGain.2': 2.6007706753846906,
          'EELayerGain.3': 2.915493036178964,
          'EELayerGain.4': 0.9648518378205662,
          'EELayerGain.5A': 2.093848044593692,
          'EELayerGain.5B': 3.513209401958356,
          'EELayerGain.6': 3.966806690354486,
          'EILayerGain.1': 4.871525353297733,
          'EILayerGain.2': 2.6757789861046226,
          'EILayerGain.3': 4.873013187584787,
          'EILayerGain.4': 0.6576721266367123,
          'EILayerGain.5A': 0.5249502250535366,
          'EILayerGain.5B': 4.070348589946223,
          'EILayerGain.6': 4.488206187954194,
          'IELayerGain.1': 2.6187628288588147,
          'IELayerGain.2': 1.496772667037593,
          'IELayerGain.3': 0.5025482778776683,
          'IELayerGain.4': 0.9289079361991758,
          'IELayerGain.5A': 4.560854053887325,
          'IELayerGain.5B': 3.8084090947786073,
          'IELayerGain.6': 4.9802544314045765,
          'IILayerGain.1': 4.357568076276535,
          'IILayerGain.2': 4.687197720855446,
          'IILayerGain.3': 3.6637924759341383,
          'IILayerGain.4': 0.1115456180822973,
          'IILayerGain.5A': 2.1481316992341473,
          'IILayerGain.5B': 0.10608943982250264,
          'IILayerGain.6': 1.0284891897514596
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

# use batch_shell_config if running directly on the machine
shell_config = {'command': 'mpiexec -np 6 nrniv -python -mpi init.py'}

# use batch_sge_config if running on Downstate HPC or other SGE systems
sge_config = {
    'job_type': 'sge',
    'comm_type': 'sfs',
    'queue': 'cpu.q',
    'output_path': str('../A1/simOutput/' + label + '/'),
    'checkpoint_path': '../A1/simOutput/ray',
    'run_config': {
        'cores': 40,
        'vmem': '128G',
        'realtime': '04:00:00',
        'command': 'mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py'
    }
}

ssh_expanse_cpu = {
    'job_type': 'ssh_slurm',
    'comm_type': 'sftp',
    'host': 'expanse',
    'key': ssh_key,  # No key needed for this host
    'remote_dir': '/home/smcelroy/A1',
    'output_path': './simOutput/' + label,
    'checkpoint_path': "./simOutput/ray",
    'run_config': {
        'allocation': 'TG-IBN140002',
        'realtime': '2:40:00',
        'partition': 'compute',
        'nodes': 1,
        'coresPerNode': 128,
        'mem': '200G',
        'custom': '',
        'email': 'scott.mcelroy@downstate.edu',
        'command': f"""
        {CONFIG_EXPANSE_CPU}
        mpirun -n 64 nrniv -python -mpi init.py
        """
    }
}

ssh_expanse_gpu = {
    'job_type': 'ssh_slurm',
    'comm_type': 'sftp',
    'host': 'expanse',
    'key': ssh_key,  # No key needed for this host
    'remote_dir': '/home/smcelroy/A1',
    'output_path': './simOutput/' + label,
    'checkpoint_path': "./simOutput/ray",
    'run_config': {
        'allocation': 'TG-IBN140002',
        'realtime': '2:40:00',
        'partition': 'gpu-shared',
        'nodes': 1,
        'coresPerNode': 16,
        'mem': '200G',
        'command': f"""
    {CONFIG_EXPANSE_GPU}
    time mpirun --bind-to none -n $SLURM_NTASKS ./x86_64/special -mpi -python init.py
    """
    }
}

run_config = sge_config
search(
    label= label,
    params=params,
    metric='loss',  # if a metric and mode is specified, the search will collect metric data and report on the optimal configuration
    mode='min',  # currently remote submissions only support projects where session data (sim.send) is implemented
    algorithm="variant_generator",
    max_concurrent=6,
    # num_samples = num_samples,
    # sample_interval = 15,
    **run_config
    )  # host alias (can use ssh tunneling through config file)
