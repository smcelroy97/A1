from copy import deepcopy
import json
import pickle

import numpy as np

from netpyne.batchtools import specs

netParams = specs.NetParams()   # object of class NetParams to store the network parameters

from cfg_new import cfg


#------------------------------------------------------------------------------
#
# NETWORK PARAMETERS
#
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# General network parameters
#------------------------------------------------------------------------------

netParams.scale = cfg.scale 
netParams.sizeX = cfg.sizeX 
netParams.sizeY = cfg.sizeY
netParams.sizeZ = cfg.sizeZ
netParams.shape = 'cylinder'

#------------------------------------------------------------------------------
# General connectivity parameters
#------------------------------------------------------------------------------
netParams.scaleConnWeight = 1.0
netParams.scaleConnWeightModels = { 'HH_reduced': 1.0, 'HH_full': 1.0}
netParams.scaleConnWeightNetStims = 1.0
netParams.defaultThreshold = 0.0
netParams.defaultDelay = 2.0
netParams.propVelocity = 500.0
netParams.probLambda = 100.0

#------------------------------------------------------------------------------
# Cell parameters
#------------------------------------------------------------------------------
layer = {'5A': [0.625, 0.667]} # normalized layer boundaries
netParams.loadCellParamsRule(label='IT5A_reduced', fileName='cells/IT5A_reduced_cellParams.json')

#------------------------------------------------------------------------------
# Population parameters
#------------------------------------------------------------------------------
with open('cells/cellDensity.pkl', 'rb') as fileObj:
    density = pickle.load(fileObj)['density']
density = {k: [x * cfg.scaleDensity for x in v] for k, v in density.items()}

netParams.popParams['IT5A'] =     {'cellType': 'IT',  'cellModel': 'HH_reduced',   'ynormRange': layer['5A'], 	'density': 0.5*density[('A1','E')][3]}

#------------------------------------------------------------------------------
# Synaptic mechanism parameters
#------------------------------------------------------------------------------
netParams.synMechParams['AMPA'] = {'mod':'MyExp2SynBB', 'tau1': 0.05, 'tau2': 5.3*cfg.AMPATau2Factor, 'e': 0}

#------------------------------------------------------------------------------
# OU current / conductance inputs
#------------------------------------------------------------------------------
with open('data/inputResistances.json', 'rb') as f:
    inpRes = json.load(f)

def _multiply(x, y):
    if np.isscalar(x):
        return x * y
    else:
        return [x_ * y for x_ in x]

netParams.NoiseOUParams = {}

for pop in cfg.allpops:
    ou_amp = _multiply(cfg.OUamp, 0.01)
    ou_std = _multiply(cfg.OUstd, 0.01)
    
    K = 70 / inpRes[pop]

    mean = _multiply(ou_amp, K)
    sigma = _multiply(ou_std, K)

    netParams.NoiseOUParams[pop] = {
        'mean': mean,
        'sigma': sigma
    }

    duration = cfg.ou_noise_duration

    src_par = {
        'type': 'IClamp',
        'dur': duration,
        'amp': 0
    }

    netParams.stimSourceParams[f'NoiseOU_source_{pop}'] = deepcopy(src_par)
    netParams.stimTargetParams[f'NoiseOU_target_{pop}'] = {
        'source': f'NoiseOU_source_{pop}',
        'sec':'soma',
        'loc': 0.5,
        'conds': {'pop': pop}
    }

#------------------------------------------------------------------------------
# NetStim inputs
#------------------------------------------------------------------------------
for pop in cfg.pops_active:
    netParams.stimSourceParams[f'bkg_src_{pop}'] = {
        'type': 'NetStim',
        'rate': cfg.bkg_spike_inputs[pop]['r'],
        'noise': 1.0,
    }
    netParams.stimTargetParams[f'bkg_targ_{pop}'] =  {
        'source': f'bkg_src_{pop}',
        'conds': {'pop': pop},
        'sec': 'apic',
        'loc': 0.5,
        'synMech': 'AMPA',
        'weight': cfg.bkg_spike_inputs[pop]['w']
    }

#------------------------------------------------------------------------------
# Modify membrane mechanisms
#------------------------------------------------------------------------------
v = cfg.mech_changes
for pop in cfg.pops_active:
    secs_all = netParams.cellParams[f'{pop}_reduced']['secs']
    if v['sec'] == 'all':
        secs = list(secs_all.values())
    else:
        secs = [secs_all[v['sec']]]
    for sec in secs:
        sec['mechs'][v['mech']][v['par']] *= v['mult']