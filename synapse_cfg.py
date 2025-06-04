from netpyne.batchtools import specs
import pickle
import json
import numpy as np
cfg = specs.SimConfig()



# These values taken from M1 cfg (https://github.com/Neurosim-lab/netpyne/blob/development/examples/M1detailed/cfg.py)
cfg.singleCellPops = False
cfg.singlePop = ''
cfg.removeWeightNorm = False
cfg.scale = 1.0  # Is this what should be used?
cfg.sizeY = 2000.0  # 1350.0 in M1_detailed # should this be set to 2000 since that is the full height of the column?
cfg.sizeX = 5.0  # 400 - This may change depending on electrode radius
cfg.sizeZ = 200.0
cfg.scaleDensity = 1.0  # Should be 1.0 unless need lower cell density for test simulation or visualization



cfg.duration = 150  # Duration of the sim, in ms
cfg.dt = 0.05  # Internal Integration Time Step
cfg.verbose = 0  # Show detailed messages
cfg.progressBar = 0  # even more detailed message
cfg.hParams['celsius'] = 37
cfg.createNEURONObj = 1
cfg.createPyStruct = 1
cfg.printRunTime = 0.1

cfg.connRandomSecFromList = False  # set to false for reproducibility
cfg.cvode_active = False
cfg.cvode_atol = 1e-6
cfg.cache_efficient = True
# cfg.printRunTime = 0.1  			## specified above
cfg.oneSynPerNetcon = False
cfg.includeParamsLabel = False
cfg.printPopAvgRates = [0, cfg.duration]  # "printPopAvgRates": [[1500,1750],[1750,2000],[2000,2250],[2250,2500]]
cfg.validateNetParams = False

# ------------------------------------------------------------------------------
# Recording
# ------------------------------------------------------------------------------
cfg.allpops = ['NGF1', 'IT2', 'SOM2', 'PV2', 'VIP2', 'NGF2', 'IT3', 'SOM3', 'PV3', 'VIP3', 'NGF3', 'ITP4', 'ITS4',
               'SOM4', 'PV4', 'VIP4', 'NGF4', 'IT5A', 'CT5A', 'SOM5A', 'PV5A', 'VIP5A', 'NGF5A', 'IT5B', 'PT5B', 'CT5B',
               'SOM5B', 'PV5B', 'VIP5B', 'NGF5B', 'IT6', 'CT6', 'SOM6', 'PV6', 'VIP6', 'NGF6', 'TC', 'TCM', 'HTC',
               'IRE', 'IREM', 'TI', 'TIM']

cfg.allCorticalPops = ['NGF1', 'IT2', 'SOM2', 'PV2', 'VIP2', 'NGF2', 'IT3', 'SOM3', 'PV3', 'VIP3', 'NGF3', 'ITP4',
                       'ITS4', 'SOM4', 'PV4', 'VIP4', 'NGF4', 'IT5A', 'CT5A', 'SOM5A', 'PV5A', 'VIP5A', 'NGF5A', 'IT5B',
                       'PT5B', 'CT5B', 'SOM5B', 'PV5B', 'VIP5B', 'NGF5B', 'IT6', 'CT6', 'SOM6', 'PV6', 'VIP6', 'NGF6']

cfg.Epops = ['IT2', 'IT3', 'ITP4', 'ITS4', 'IT5A', 'CT5A', 'IT5B', 'CT5B' , 'PT5B', 'IT6', 'CT6']  # all layers

cfg.Ipops = ['NGF1',                            # L1
        'PV2', 'SOM2', 'VIP2', 'NGF2',      # L2
        'PV3', 'SOM3', 'VIP3', 'NGF3',      # L3
        'PV4', 'SOM4', 'VIP4', 'NGF4',      # L4
        'PV5A', 'SOM5A', 'VIP5A', 'NGF5A',  # L5A
        'PV5B', 'SOM5B', 'VIP5B', 'NGF5B',  # L5B
        'PV6', 'SOM6', 'VIP6', 'NGF6']      # L6

cfg.TEpops = ['TC', 'TCM', 'HTC']

cfg.TIpops = ['IRE', 'IREM', 'TI', 'TIM']

cfg.pops_active = ['IT2']

if cfg.pops_active:
    cfg.allpops = cfg.pops_active

# Dict with traces to record -- taken from M1 cfg.py
cfg.recordTraces = {'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}
                    # 'g_NMDA': {'sec':'soma', 'loc':0.5, 'synMech':'NMDA', 'var':'g'},
                    # 'g_GABAB': {'sec':'soma', 'loc':0.5, 'synMech':'GABAB', 'var':'g'}
}
cfg.recordStim = False  # Seen in M1 cfg.py
cfg.recordTime = True  # SEen in M1 cfg.py
cfg.recordStep = 0.05  # Step size (in ms) to save data -- value from M1 cfg.py

cfg.recordLFP = [[100, y, 100] for y in range(0, 2000, 100)]
cfg.recordDipole = False

# ------------------------------------------------------------------------------
# Saving
# ------------------------------------------------------------------------------

cfg.simLabel = 'PSPTest'
cfg.saveFolder = 'simOutput/' + cfg.simLabel  # Set file output name
cfg.savePickle = True  # Save pkl file
cfg.saveJson = False  # Save json file
cfg.saveDataInclude = ['simData', 'simConfig', 'net', 'netParams',  'netCells', 'netPops']
cfg.backupCfgFile = None
cfg.gatherOnlySimData = False
cfg.saveCellSecs = False
cfg.saveCellConns = True
cfg.addNoiseIClamp = False

# ------------------------------------------------------------------------------
# Analysis and plotting
# ------------------------------------------------------------------------------

# cfg.analysis['plotRaster'] = {'include': cfg.allpops, 'saveFig': True, 'showFig': False, 'orderInverse': True, # 'figSize': (25, 25),
#                               'markerSize': 50}   # Plot a raster

# cfg.analysis['plotConn'] = {'includePre': cfg.allpops, 'includePost': ['TC'], 'feature': 'strength',
#                             'saveFig': True, 'showFig': False, 'figSize': (25, 25)}  # Plot conn matrix
# 'include': [('TC', i) for i in range(40)],

cfg.analysis['plotTraces'] = {'include': cfg.allpops, 'timeRange': [0, cfg.duration],
'oneFigPer': 'trace', 'overlay': True, 'saveFig': False, 'showFig': False, 'figSize':(12,8)}

def setplotTraces (ncell=1, linclude=[]):
  for pop in cfg.allpops:
    for i in range(ncell):
      linclude.append( (pop,i) )
  cfg.analysis['plotTraces'] = {'include': linclude, 'oneFigPer': 'trace', 'overlay': True, 'saveFig': True, 'showFig': False, 'figSize':(12,8)}

# setplotTraces(ncell=20, linclude=['IT2'])

layer_bounds = {'L1': 100, 'L2': 160, 'L3': 950, 'L4': 1250, 'L5A': 1334, 'L5B': 1550, 'L6': 2000}

# full weight conn matrix
with open('conn/conn.pkl', 'rb') as fileObj:
    connData = pickle.load(fileObj)
cfg.wmat = connData['wmat']

cfg.seeds = {'conn': 23451, 'stim': 1, 'loc': 1}

# ------------------------------------------------------------------------------

cfg.weightNormThreshold = 5.0  # maximum weight normalization factor with respect to the soma
cfg.weightNormScaling = {'NGF_reduced': 1.0, 'ITS4_reduced': 1.0}
cfg.ihGbar = 1.0
cfg.KgbarFactor = 1.0
# ------------------------------------------------------------------------------
# Synapses
# ------------------------------------------------------------------------------

# General Synaptic Parameters
cfg.synWeightFractionEE = [0.5, 0.5]  # E->E AMPA to NMDA ratio
cfg.synWeightFractionEI = [0.5, 0.5]  # E->I AMPA to NMDA ratio
cfg.synWeightFractionIE = [0.9, 0.1]
cfg.synWeightFractionII = [1.0]

cfg.synWeightFractionEI_CustomCort = [0.5, 0.5]  # E->I AMPA to NMDA ratio custom for cortex NMDA manipulation

# SST Synapses
cfg.synWeightFractionSOME = [0.9, 0.2]  # SOM -> E GABAASlow to GABAB ratio
cfg.synWeightFractionSOMI = [0.9, 0.1]  # SOM -> I GABAASlow to GABAB ratio

# NGF synapses
cfg.synWeightFractionNGF = [0.5, 0.9]  # NGF GABAA to GABAB ratio
cfg.synWeightFractionNGFE = [0.5, 1.0]
cfg.synWeightFractionNGFI = [1.0]
cfg.synWeightFractionENGF = [0.834, 0.166]  # NGF AMPA to NMDA ratio

cfg.useHScale = False

# Thalamic Synaptic Parameters
cfg.synWeightFractionThalIE = [0.9, 0.2]
cfg.synWeightFractionThalII = [1.0, 0.0]
cfg.synWeightFractionThalCtxII = [1.0]
cfg.synWeightFractionThalCtxIE = [1.0, 0.0]

cfg.tune = {}
cfg.update_cfg()
