from netpyne.batchtools.search import search
import numpy as np


initCfg = {}

filename = 'data/v34_batch25/trial_2142/trial_2142_cfg.json'

# from prev
import json

with open(filename, 'rb') as f:
       cfgLoad = json.load(f)['simConfig']
cfgLoad2 = cfgLoad

params = {'EEGain' : np.linspace(0.5, 1.5, 2),
          'IEGain' : np.linspace(0.5, 1.5, 2),
}

# updateParams = {'EEGain', 'EIGain','IEGain', 'IIGain'
#                 'EICellTypeGain.PV', 'EICellTypeGain.SOM', 'EICellTypeGain.VIP', 'EICellTypeGain.NGF',
#                 'IECellTypeGain.PV', 'IECellTypeGain.SOM', 'IECellTypeGain.VIP', 'IECellTypeGain.NGF',
#                 'EILayerGain.1', 'IILayerGain.1',
#                 'EELayerGain.2', 'EILayerGain.2', 'IELayerGain.2', 'IILayerGain.2',
#                 'EELayerGain.3', 'EILayerGain.3', 'IELayerGain.3', 'IILayerGain.3',
#                 'EELayerGain.4', 'EILayerGain.4', 'IELayerGain.4', 'IILayerGain.4',
#                 'EELayerGain.5A', 'EILayerGain.5A', 'IELayerGain.5A', 'IILayerGain.5A',
#                 'EELayerGain.5B', 'EILayerGain.5B', 'IELayerGain.5B', 'IILayerGain.5B',
#                 'EELayerGain.6', 'EILayerGain.6', 'IELayerGain.6', 'IILayerGain.6'}

updateParams = ['IIGain', 'EIGain',
       ('EICellTypeGain', 'PV'), ('EICellTypeGain', 'SOM'),
       ('EICellTypeGain', 'VIP'), ('EICellTypeGain', 'NGF'),
       ('IECellTypeGain', 'PV'), ('IECellTypeGain', 'SOM'), ('IECellTypeGain', 'VIP'),
       ('IECellTypeGain', 'NGF'),
       ('EILayerGain', '1'), ('IILayerGain', '1'),
       ('EELayerGain', '2'), ('EILayerGain', '2'), ('IELayerGain', '2'), ('IILayerGain', '2'),
       ('EELayerGain', '3'), ('EILayerGain', '3'), ('IELayerGain', '3'), ('IILayerGain', '3'),
       ('EELayerGain', '4'), ('EILayerGain', '4'), ('IELayerGain', '4'), ('IILayerGain', '4'),
       ('EELayerGain', '5A'), ('EILayerGain', '5A'), ('IELayerGain', '5A'), ('IILayerGain', '5A'),
       ('EELayerGain', '5B'), ('EILayerGain', '5B'), ('IELayerGain', '5B'), ('IILayerGain', '5B'),
       ('EELayerGain', '6'), ('EILayerGain', '6'), ('IELayerGain', '6'), ('IILayerGain', '6')]
# Things removed for tuning, put back when finished, or update value:
# 'EIGain', 'IEGain', 'IIGain', 'EEGain', ('IELayerGain', '6') ('EILayerGain', '4') ('IILayerGain', '4')


for p in updateParams:
       if isinstance(p, tuple):
              initCfg.update({p: cfgLoad[p[0]][p[1]]})
       else:
              initCfg.update({p: cfgLoad[p]})

    # good thal params for 100% cell density
updateParams2 = ['wmat']

for p in updateParams2:
       if isinstance(p, tuple):
              initCfg.update({p: cfgLoad2[p[0]][p[1]]})
       else:
              initCfg.update({p: cfgLoad2[p]})


# use batch_shell_config if running directly on the machine
shell_config = {'command': 'mpiexec -np 4 nrniv -python -mpi init.py',}

# use batch_sge_config if running on Downstate HPC or other SGE systems
sge_config = {
    'queue': 'cpu.q',
    'cores': 64,
    'vmem': '256G',
    'realtime': '01:45:00',
    'command': 'mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py'}

run_config = sge_config

search(job_type = 'sge',
       comm_type = 'socket',
       label = 'grid',
       params = params,
       output_path = '../A1model_sm/data/grid_batch',
       checkpoint_path = '../A1model_sm/data/ray',
       run_config = run_config,
       num_samples = 1,
       metric = 'loss',
       mode = 'min',
       algorithm = "variant_generator",
       max_concurrent = 9)
