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

    if not filename:
        filename = 'data/v34_batch25/trial_2142/trial_2142_cfg.json'

    # from prev
    import json
    with open(filename, 'rb') as f:
        cfgLoad = json.load(f)['simConfig']
    cfgLoad2 = cfgLoad

    #### SET weights####

    params['IELayerGain', '6'] = [4.9]
    params['EELayerGain', '6'] = [0.6]
    params['EILayerGain', '4'] = [0.7]
    params['IILayerGain', '4'] = [1.08]

    # --------------------------------------------------------
    
    # grouped params
    groupedParams = []

    # initial config
    initCfg = {}

    # from prev - best of 50% cell density
    updateParams = ['IEGain', 'IIGain',
                    ('EICellTypeGain', 'PV'), ('EICellTypeGain', 'SOM'),('EICellTypeGain', 'VIP'),
                    ('EICellTypeGain', 'NGF'),('IECellTypeGain', 'PV'), ('IECellTypeGain', 'SOM'),
                    ('IECellTypeGain', 'VIP'),('IECellTypeGain', 'NGF'),
                    ('EILayerGain', '1'), ('IILayerGain', '1'),
                    ('EELayerGain', '2'), ('EILayerGain', '2'),  ('IELayerGain', '2'), ('IILayerGain', '2'),
                    ('EELayerGain', '3'), ('EILayerGain', '3'), ('IELayerGain', '3'), ('IILayerGain', '3'),
                    ('EELayerGain', '4'),('IELayerGain', '4'),
                    ('EELayerGain', '5A'), ('EILayerGain', '5A'), ('IELayerGain', '5A'), ('IILayerGain', '5A'),
                    ('EELayerGain', '5B'), ('EILayerGain', '5B'), ('IELayerGain', '5B'), ('IILayerGain', '5B'),
                    ('EILayerGain', '6'), ('IILayerGain', '6')]
                    # Things removed for tuning, put back when finished, or update value:
                    # 'EIGain', 'IEGain', 'IIGain', 'EEGain', ('IELayerGain', '6') ('EILayerGain', '4') ('IILayerGain', '4')

    for p in updateParams:
        if isinstance(p, tuple):
            initCfg.update({p: cfgLoad[p[0]][p[1]]})
        else:
            initCfg.update({p: cfgLoad[p]})

    # good thal params for 100% cell density
    updateParams2 = ['wmat'] # thalamoCorticalGain', 'intraThalamicGain', 'EbkgThalamicGain', 'IbkgThalamicGain',

    for p in updateParams2:
        if isinstance(p, tuple):
            initCfg.update({p: cfgLoad2[p[0]][p[1]]})
        else:
            initCfg.update({p: cfgLoad2[p]})



    b = Batch(params=params, netParamsFile='netParams.py', cfgFile='cfg.py', initCfg=initCfg, groupedParams=groupedParams)
    b.method = 'grid'

    return b


# ----------------------------------------------------------------------------------------------
# Evol
# ----------------------------------------------------------------------------------------------
def evolRates(filename):
    # --------------------------------------------------------
    # parameters
    params = specs.ODict()

    if not filename:
        filename = 'data/v34_batch25/trial_2142/trial_2142_cfg.json'

    # from prev
    import json
    with open(filename, 'rb') as f:
        cfgLoad = json.load(f)['simConfig']
    cfgLoad2 = cfgLoad

    params['EEGain'] = [0.5, 1.5]
    params['EIGain'] = [0.9, 1.75]
    params['IEGain'] = [0.9, 1.75]
    params['IIGain'] = [0.5, 1.5]

    groupedParams = []

    # --------------------------------------------------------
    # initial config

    initCfg = {} # set default options from prev sim

    initCfg['duration'] = 6000 #11500
    initCfg['printPopAvgRates'] = [3000, 6000]
    initCfg['scaleDensity'] = 1.0
    initCfg['recordStep'] = 0.05

    # SET SEEDS FOR CONN AND STIM
    initCfg[('seeds', 'conn')] = 0

    ### OPTION TO RECORD EEG / DIPOLE ###
    initCfg['recordDipole'] = True
    initCfg['saveCellSecs'] = False
    initCfg['saveCellConns'] = False


    # from prev - best of 50% cell density
    updateParams = [('EICellTypeGain', 'PV'), ('EICellTypeGain', 'SOM'), ('EICellTypeGain', 'VIP'),
                    ('EICellTypeGain', 'NGF'),
                    ('IECellTypeGain', 'PV'), ('IECellTypeGain', 'SOM'), ('IECellTypeGain', 'VIP'),
                    ('IECellTypeGain', 'NGF'),
                    ('EILayerGain', '1'), ('IILayerGain', '1'),
                    ('EELayerGain', '2'), ('EILayerGain', '2'),  ('IELayerGain', '2'), ('IILayerGain', '2'),
                    ('EELayerGain', '3'), ('EILayerGain', '3'), ('IELayerGain', '3'), ('IILayerGain', '3'),
                    ('EELayerGain', '4'), ('EILayerGain', '4'), ('IELayerGain', '4'), ('IILayerGain', '4'),
                    ('EELayerGain', '5A'), ('EILayerGain', '5A'), ('IELayerGain', '5A'), ('IILayerGain', '5A'),
                    ('EELayerGain', '5B'), ('EILayerGain', '5B'), ('IELayerGain', '5B'), ('IILayerGain', '5B'),
                    ('EELayerGain', '6'), ('EILayerGain', '6'), ('IELayerGain', '6'), ('IILayerGain', '6')]

    for p in updateParams:
        if isinstance(p, tuple):
            initCfg.update({p: cfgLoad[p[0]][p[1]]})
        else:
            initCfg.update({p: cfgLoad[p]})

    # good thal params for 100% cell density
    updateParams2 = ['thalamoCorticalGain', 'intraThalamicGain', 'EbkgThalamicGain', 'IbkgThalamicGain', 'wmat']

    for p in updateParams2:
        if isinstance(p, tuple):
            initCfg.update({p: cfgLoad2[p[0]][p[1]]})
        else:
            initCfg.update({p: cfgLoad2[p]})
    # --------------------------------------------------------
    # fitness function
    fitnessFuncArgs = {}
    pops = {}

    ## Exc pops
    Epops = ['IT2', 'IT3', 'ITP4', 'ITS4', 'IT5A', 'CT5A', 'IT5B', 'CT5B', 'PT5B', 'IT6', 'CT6']

    Etune = {'target': 5, 'width': 5, 'min': 0.5}
    for pop in Epops:
        pops[pop] = Etune

    ## Inh pops
    Ipops = ['NGF1',  # L1
             'PV2', 'SOM2', 'VIP2', 'NGF2',  # L2
             'PV3', 'SOM3', 'VIP3', 'NGF3',  # L3
             'PV4', 'SOM4', 'VIP4', 'NGF4',  # L4
             'PV5A', 'SOM5A', 'VIP5A', 'NGF5A',  # L5A
             'PV5B', 'SOM5B', 'VIP5B', 'NGF5B',  # L5B
             'PV6', 'SOM6', 'VIP6', 'NGF6']  # L6

    Itune = {'target': 10, 'width': 15, 'min': 0.25}
    for pop in Ipops:
        pops[pop] = Itune

    fitnessFuncArgs['pops'] = pops
    fitnessFuncArgs['maxFitness'] = 1000

    def fitnessFunc(simData, **kwargs):
        pops = kwargs['pops']
        maxFitness = kwargs['maxFitness']
        popFitness = [min(np.exp(abs(v['target'] - simData['popRates'][k]) / v['width']), maxFitness)
                      if simData['popRates'][k] > v['min'] else maxFitness for k, v in pops.items()]
        fitness = np.mean(popFitness)

        popInfo = '; '.join(
            ['%s rate=%.1f fit=%1.f' % (p, simData['popRates'][p], popFitness[i]) for i, p in enumerate(pops)])
        print('  ' + popInfo)
        return fitness

    # from IPython import embed; embed()

    b = Batch(params=params, groupedParams=groupedParams, initCfg=initCfg)
    b.method = 'evol'

    # Set evol alg configuration
    b.evolCfg = {
        'evolAlgorithm': 'custom',
        'fitnessFunc': fitnessFunc,  # fitness expression (should read simData)
        'fitnessFuncArgs': fitnessFuncArgs,
        'pop_size': 10,
        'num_elites': 2,
        'mutation_rate': 0.5,
        'crossover': 0.5,
        'maximize': False,  # maximize fitness function?
        'max_generations': 50,
        'time_sleep': 5 * 300,  # 5min wait this time before checking again if sim is completed (for each generation)
        'maxiter_wait': 10 * 64,  # (5h20) max number of times to check if sim is completed (for each generation)
        'defaultFitness': 1000,  # set fitness value in case simulation time is over
        'scancelUser': 'ext_scottmcelroy54_gmail_com'
    }

    return b


# ----------------------------------------------------------------------------------------------
# Run configurations
# ----------------------------------------------------------------------------------------------
def setRunCfg(b, type='hpc_sge'):
    if type == 'hpc_sge':
        b.runCfg = {'type': 'hpc_sge', # for downstate HPC
                    'jobName': 'smc_ASSR_batch', # label for job
                    'cores': 64, # give 60 cores here
                    'script': 'init.py', # what you normally run
                    'vmem': '256G', # or however much memory you need
                    'walltime': '2:15:00', # make 2 hours or something
                    'skip': True}
    elif type == 'hpc_slurm_Expanse':
        b.runCfg = {'type': 'hpc_slurm',
                    'allocation': 'TG-IBN140002',
                    'partition': 'shared',
                    'walltime': '2:00:00',
                    'nodes': 1,
                    'coresPerNode': 64,
                    'email': 'scott.mcelroy@downstate.edu',
                    'folder': '/home/smcelroy/A1model_sm/',
                    'script': 'init.py',
                    'mpiCommand': 'mpirun',
                    'custom': '#SBATCH --constraint="lustre"\n#SBATCH --export=ALL\n#SBATCH --partition=compute',
                    'skip': True,
                    'skipCustom': '_data.pkl'}

    elif type == 'hpc_slurm_JUSUF':
        b.runCfg = {'type': 'hpc_slurm',
                    'allocation': 'TG-IBN140002',
                    'partition': 'compute',
                    'walltime': '1:40:00',
                    'nodes': 1,
                    'coresPerNode': 128,
                    'email': 'scott.mcelroy@downstate.edu',
                    'folder': '/home/smcelroy/A1model_sm/',
                    'script': 'init.py',
                    'mpiCommand': 'mpirun',
                    'custom': '\n#SBATCH --export=ALL\n#SBATCH --partition=compute',
                   # 'custom': '#SBATCH --constraint="lustre"\n#SBATCH --export=ALL\n#SBATCH --partition=compute',
                    'skip': True,
                    'skipCustom': '_data.pkl'}

    elif type=='mpi_direct':
        b.runCfg = {'type': 'mpi_direct',
                    'cores': 1,
                    'script': 'init.py',
                    'mpiCommand': 'mpirun', # --use-hwthread-cpus
                    'skip': True}
    # ------------------------------


# ----------------------------------------------------------------------------------------------
# Main code
# ----------------------------------------------------------------------------------------------

if __name__ == '__main__':

    b = assr_batch_grid('data/v34_batch25/trial_2142/trial_2142_cfg.json')
    # b = evolRates('data/v34_batch25/trial_2142/trial_2142_cfg.json')
    #
    # b.batchLabel = 'SamParams0814b'
    # b.saveFolder = 'data/'+b.batchLabel
    #
    # setRunCfg(b, 'hpc_slurm_Expanse')
    # b.run() # run batch

    b.batchLabel = 'SpontOnOffFreqTest0827'
    b.saveFolder = 'data/'+b.batchLabel

    setRunCfg(b, 'hpc_sge')
    b.run() # run batch
