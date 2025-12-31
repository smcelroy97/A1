from copy import deepcopy
import json
import pickle

import numpy as np

from netpyne.batchtools import specs

netParams = specs.NetParams()   # object of class NetParams to store the network parameters

from cfg_new import cfg

POP = 'IT5A'
#------------------------------------------------------------------------------
#
# NETWORK PARAMETERS
#
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# General network parameters
#------------------------------------------------------------------------------

netParams.scale = 1.0
netParams.sizeX = 200.0
netParams.sizeY = 2000.0
netParams.sizeZ = 200.0
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
netParams.loadCellParamsRule(label='IT5A_reduced', fileName='cells/IT5A_reduced_cellParams.json')

#------------------------------------------------------------------------------
# Population parameters
#------------------------------------------------------------------------------

# scaleDensity is 1.
netParams.popParams[POP] = {
    'cellType': 'IT',
    'cellModel': 'HH_reduced',
    'ynormRange': [0.625, 0.667], # probably don't need this either
    'density': 0.5 * 272160.0}

# density[('A1', 'E')]
# Out[3]: [0.0, 179784.0, 177744.0, 272160.0, 208413.0, 142870.0]
# In [4]: density[('A1', 'E')][3]
# Out[4]: 272160.0

#------------------------------------------------------------------------------
# Synaptic mechanism parameters
#------------------------------------------------------------------------------
netParams.synMechParams['AMPA'] = {'mod':'MyExp2SynBB', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}

#------------------------------------------------------------------------------
# OU current / conductance inputs
#------------------------------------------------------------------------------

# In [7]: with open('data/inputResistances.json', 'rb') as f:
#    ...:     res = json.load(f)
#    ...:
#
# In [8]: res['IT5A']
# Out[8]: 0.044510289788146154


netParams.stimSourceParams[f'NoiseOU_source_{POP}'] = {
    'type': 'IClamp',
    'dur': cfg.ou_noise_duration,
    'amp': 0
}
netParams.stimTargetParams[f'NoiseOU_target_{POP}'] = {
        'source': f'NoiseOU_source_{POP}',
        'sec':'soma',
        'loc': 0.5,
        'conds': {'pop': POP}
}

#------------------------------------------------------------------------------
# NetStim inputs
#------------------------------------------------------------------------------

netParams.stimSourceParams[f'bkg_src_{POP}'] = {
    'type': 'NetStim',
    'rate': cfg.bkg_r,
    'noise': 1.0,
}
netParams.stimTargetParams[f'bkg_targ_{POP}'] =  {
    'source': f'bkg_src_{POP}',
    'conds': {'pop': POP},
    'sec': 'apic',
    'loc': 0.5,
    'synMech': 'AMPA',
    'weight': cfg.bkg_w,
}

#------------------------------------------------------------------------------
# Modify membrane mechanisms
#------------------------------------------------------------------------------
v = cfg.mech_changes

def multiply_parameters_func(pop: str,
                             secs: list,
                             mech: str,
                             parameter: str,
                             factor: int|float):
    _pop = netParams.popParams[pop]
    for sec in secs:
        _pop['secs'][sec]['mechs'][mech][parameter] *= factor

for rule in cfg.multiply_parameter:
    multiply_parameters_func(pop=f"{POP}", **cfg.multiply_parameters[rule])