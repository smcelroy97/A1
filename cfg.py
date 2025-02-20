"""
cfg.py

Simulation configuration for A1 model (using NetPyNE)
This file has sim configs as well as specification for parameterized values in netParams.py

Contributors: ericaygriffith@gmail.com, salvadordura@gmail.com, samnemo@gmail.com
"""
from netpyne.batchtools import specs
import pickle
import json
import numpy as np
cfg = specs.SimConfig()

# ------------------------------------------------------------------------------
#
# SIMULATION CONFIGURATION
#
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Run parameters
# ------------------------------------------------------------------------------
cfg.duration = 3000  # Duration of the sim, in ms
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
# cfg.printPopAvgRates = [1000, 2000]  # "printPopAvgRates": [[1500,1750],[1750,2000],[2000,2250],[2250,2500]]
cfg.validateNetParams = False

# ------------------------------------------------------------------------------
# Recording
# ------------------------------------------------------------------------------
cfg.allpops = ['NGF1', 'IT2', 'SOM2', 'PV2', 'VIP2', 'NGF2', 'IT3', 'SOM3', 'PV3', 'VIP3', 'NGF3', 'ITP4', 'ITS4',
               'SOM4', 'PV4', 'VIP4', 'NGF4', 'IT5A', 'CT5A', 'SOM5A', 'PV5A', 'VIP5A', 'NGF5A', 'IT5B', 'CT5B', 'PT5B',
               'SOM5B', 'PV5B', 'VIP5B', 'NGF5B', 'IT6', 'CT6', 'SOM6', 'PV6', 'VIP6', 'NGF6', 'TC', 'TCM', 'HTC',
               'IRE', 'IREM', 'TI', 'TIM']

cfg.allCorticalPops = ['NGF1', 'IT2', 'SOM2', 'PV2', 'VIP2', 'NGF2', 'IT3', 'SOM3', 'PV3', 'VIP3', 'NGF3', 'ITP4',
                       'ITS4', 'SOM4', 'PV4', 'VIP4', 'NGF4', 'IT5A', 'CT5A', 'SOM5A', 'PV5A', 'VIP5A', 'NGF5A', 'IT5B',
                       'PT5B', 'CT5B', 'SOM5B', 'PV5B', 'VIP5B', 'NGF5B', 'IT6', 'CT6', 'SOM6', 'PV6', 'VIP6', 'NGF6']

cfg.allThalPops = ['TC', 'TCM', 'HTC', 'IRE', 'IREM', 'TI', 'TIM']

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

# Dict with traces to record -- taken from M1 cfg.py
cfg.recordTraces = {'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}
                    # 'g_NMDA': {'sec':'soma', 'loc':0.5, 'synMech':'NMDA', 'var':'g'},
                    # 'g_GABAB': {'sec':'soma', 'loc':0.5, 'synMech':'GABAB', 'var':'g'}
}
cfg.recordStim = False  # Seen in M1 cfg.py
cfg.recordTime = True  # SEen in M1 cfg.py
cfg.recordStep =  0.05  # St ep size (in ms) to save data -- value from M1 cfg.py

cfg.recordLFP = False # [[100, y, 100] for y in range(0, 2000, 100)]
cfg.recordDipole = False

# ------------------------------------------------------------------------------
# Saving
# ------------------------------------------------------------------------------

cfg.simLabel = 'inverse1000000'
cfg.saveFolder = 'simOutput/' + cfg.simLabel  # Set file output name
cfg.savePickle = True  # Save pkl file
cfg.saveJson = False  # Save json file
cfg.saveDataInclude = ['simData', 'simConfig', 'net', 'netParams',  'netCells', 'netPops']
cfg.backupCfgFile = None
cfg.gatherOnlySimData = False
cfg.saveCellSecs = False
cfg.saveCellConns = False

# ------------------------------------------------------------------------------
# Analysis and plotting
# ------------------------------------------------------------------------------

cfg.analysis['plotRaster'] = {'include': cfg.allpops, 'saveFig': True, 'showFig': False, 'orderInverse': True, 'figSize': (25, 25),
                              'markerSize': 1}   # Plot a raster

# cfg.analysis['plotSpikeStats'] = {'stats' : ['isicv'], 'saveFig' : True}

# cfg.analysis['plotTraces'] = {'include': cfg.allpops, 'timeRange': [0, cfg.duration],
# 'oneFigPer': 'cell', 'overlay': True, 'saveFig': False, 'showFig': False, 'figSize':(12,8)}


def setplotTraces (ncell=50, linclude=cfg.allpops, timeRange = cfg.duration):
  pops = []
  for pop in linclude:
    for i in range(ncell):
      pops.append((pop,i))
  cfg.analysis['plotTraces'] = {'include': linclude, 'timeRange' : timeRange, 'oneFigPer': 'trace', 'overlay': True, 'saveFig': False, 'showFig': False, 'figSize':(12,8)}

# setplotTraces(ncell=1, timeRange=[1750, 3000])

layer_bounds = {'L1': 100, 'L2': 160, 'L3': 950, 'L4': 1250, 'L5A': 1334, 'L5B': 1550, 'L6': 2000}


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

# ------------------------------------------------------------------------------
# Network
# ------------------------------------------------------------------------------

# Insert params from previous tuning
# Insert params from previous tuning
with open('data/initCfg.json', 'rb') as f:
    cfgLoad = json.load(f)

for key, value in cfgLoad.items():
    setattr(cfg, key, value)

# These values taken from M1 cfg (https://github.com/Neurosim-lab/netpyne/blob/development/examples/M1detailed/cfg.py)
cfg.singleCellPops = False
cfg.reducedPop = False    # insert number to declare specific number of populations, if going for full model set to False
cfg.singlePop = ''
cfg.removeWeightNorm = False
cfg.scale = 1.0  # Is this what should be used?
cfg.sizeY = 2000.0  # 1350.0 in M1_detailed # should this be set to 2000 since that is the full height of the column?
cfg.sizeX = 200.0  # 400 - This may change depending on electrode radius
cfg.sizeZ = 200.0
cfg.scaleDensity = 1.0  # Should be 1.0 unless need lower cell density for test simulation or visualization

# ------------------------------------------------------------------------------
# Connectivity
# ------------------------------------------------------------------------------

# Cortical
cfg.addConn = 0
cfg.addSubConn = 1.0
cfg.wireCortex = 1.0

# cfg.EEGain = 0.75
# cfg.EIGain = 1.5
# cfg.IEGain = 1.5
# cfg.IIGain = 1.0

cfg.EEGain = 1.31667
cfg.EIGain = 1.6313576020869256
cfg.IEGain = 0.6
cfg.IIGain = 1.4102431748127964

## E/I->E/I layer weights (L1-3, L4, L5, L6)
cfg.EELayerGain = {'1': 1.0, '2': 1.0, '3': 1.0, '4': 1.0, '5A': 1.0, '5B': 1.0, '6': 1.0}
cfg.EILayerGain = {'1': 1.0, '2': 1.0, '3': 1.0, '4': 1.0, '5A': 1.0, '5B': 1.0, '6': 1.0}
cfg.IELayerGain = {'1': 1.0, '2': 1.0, '3': 1.0, '4': 1.0, '5A': 1.0, '5B': 1.0, '6': 1.0}
cfg.IILayerGain = {'1': 1.0, '2': 1.0, '3': 1.0, '4': 1.0, '5A': 1.0, '5B': 1.0, '6': 1.0}

# E -> E based on postsynaptic cortical E neuron population
cfg.EEPopGain = {"IT2": 1.3125, "IT3": 1.55, "ITP4": 1.0, "ITS4": 1.0, "IT5A": 1.05,
                 "CT5A": 1.1500000000000001, "IT5B": 0.425, "CT5B": 1.1500000000000001,
                 "PT5B": 1.05, "IT6": 1.05, "CT6": 1.05}  # this is from after generation 203 of optunaERP_23dec23_

# gains from E -> I based on postsynaptic cortical I neuron population
cfg.EIPopGain = {"NGF1": 1.0, "SOM2": 1.0, "PV2": 1.0, "VIP2": 1.0, "NGF2": 1.0, "SOM3": 1.0, "PV3": 1.0, "VIP3": 1.0,
                 "NGF3": 1.0, "SOM4": 1.0, "PV4": 1.0, "VIP4": 1.0, "NGF4": 1.0, "SOM5A": 1.0, "PV5A": 1.4,
                 "VIP5A": 1.25, "NGF5A": 0.8, "SOM5B": 1.0, "PV5B": 1.45, "VIP5B": 1.4, "NGF5B": 0.9500000000000001,
                 "SOM6": 1.0, "PV6": 1.4, "VIP6": 1.3499999999999999, "NGF6": 0.65}

## E->I by target cell type
cfg.EICellTypeGain = {'PV': 1.0, 'SOM': 1.0, 'VIP': 1.0,
                      'NGF': 1.0}

# I->E by target cell type
cfg.IECellTypeGain = {'PV': 1.0, 'SOM': 1.0, 'VIP': 1.0, 'NGF': 1.0}

# Thalamic
cfg.addIntraThalamicConn = 1.0
cfg.addCorticoThalamicConn = 1.0
cfg.addThalamoCorticalConn = 1.0

cfg.thalamoCorticalGain = 1.0
cfg.intraThalamicGain = 1.0
cfg.corticoThalamicGain = 1.0
cfg.CTGainThalI = 1.0

cfg.intraThalamicEEGain = 1.0
cfg.intraThalamicEIGain = 0.3
cfg.intraThalamicIEGain = 0.1
cfg.intraThalamicIIGain = 1.0

# these params control cochlea -> Thalamus
cfg.cochThalweightECore = 0.225  #1.0  # 0.1125
cfg.cochThalprobECore = 0.3
cfg.cochThalweightICore = 0.0675
cfg.cochThalprobICore =  0.15 #0.5
cfg.cochThalMatrixCoreFactor = 0.1
cfg.cochthalweightEMatrix = 0.1125
cfg.cochthalweightIMatrix = 0.0675
cfg.cochThalprobEMatrix = 0.0375
cfg.cochThalprobIMatrix = 0.009375
cfg.cochThalFreqRange = [750, 1250]

# Control the strength of thalamic inputs to different subpopulations
cfg.thalL4PV = 0.21367245896786016
cfg.thalL4SOM = 0.24260966747847523
cfg.thalL4E = 2.0 #1.9540886147587417

cfg.thalL4VIP = 1.0
cfg.thalL4NGF = 1.0
cfg.L3L3scaleFactor = 1.0
cfg.CT6ScaleFactor = 1.0

cfg.ITS4Type = 'ITS4'

cfg.thalL1NGF = 1.0
cfg.ENGF1 = 1.0

# L4 -> L3 Inhib pops
cfg.L4L3E = 1.0
cfg.L4L3PV = 1.0
cfg.L4L3SOM = 1.0
cfg.L4L3VIP = 1.0
cfg.L4L3NGF = 1.0
cfg.L4L4E = 1.0

# L3 -> L4 Inhib pops
cfg.L3L4PV = 1.0
cfg.L3L4SOM = 1.0

# full weight conn matrix
with open('conn/conn.pkl', 'rb') as fileObj:
    connData = pickle.load(fileObj)
cfg.wmat = connData['wmat']

cfg.seeds = {'conn': 23451, 'stim': 1, 'loc': 1}
# ------------------------------------------------------------------------------
# Background inputs
# ------------------------------------------------------------------------------
cfg.addBkgConn = 0
cfg.noiseBkg = 0  # firing rate random noise
cfg.delayBkg = 5.0  # (ms)
cfg.startBkg = 0  # start at 0 ms
cfg.rateBkg = {'exc': 40, 'inh': 40}

cfg.EbkgThalamicGain = 1.04528
cfg.IbkgThalamicGain = 0.485714
cfg.BkgCtxEGain = 1.4285714285714286
cfg.BkgCtxIGain = 0.8285714285714285

cfg.NGF6bkgGain = 1.0

cfg.cochlearThalInput = False
# parameters to generate realistic  auditory thalamic inputs using Brian Hears


if cfg.cochlearThalInput:
    cfg.cochlearThalInput = {"lonset" : [0], "numCenterFreqs": 100, "freqRange":[125, 20000], "loudnessScale": 1,
                             "lfnwave": ["wav/silence6.5s.wav"]}
    cfg.cochlearThalInput['probECore'] = cfg.cochThalprobECore
    cfg.cochlearThalInput['weightECore'] = cfg.cochThalweightECore
    cfg.cochlearThalInput['probICore'] = cfg.cochThalprobICore
    cfg.cochlearThalInput['weightICore'] = cfg.cochThalweightICore
    cfg.cochlearThalInput['weightEMatrix'] = cfg.cochthalweightEMatrix
    cfg.cochlearThalInput['weightIMatrix'] = cfg.cochthalweightIMatrix
    cfg.cochlearThalInput['probEMatrix'] = cfg.cochThalprobEMatrix
    cfg.cochlearThalInput['probIMatrix'] = cfg.cochThalprobIMatrix
    cfg.cochlearThalInput['MatrixCoreFactor'] = cfg.cochThalMatrixCoreFactor
else:
    cfg.cochlearThalInput = False


# ------------------------------------------------------------------------------
# Current inputs
# ------------------------------------------------------------------------------
# The way this is set up now is to make F-I curves for each population but can be used for other purposes
# Just needs to be modified for the specific use
cfg.addIClamp = 0
cfg.numInjections = 13
cfg.injectionInterval = 3000  # 1 second in ms
cfg.injectionDuration = 1000  # 1 second in ms
cfg.injectionAmplitudes =  np.linspace(0.0, 0.6, 13)

cfg.addNoiseConductance = 1

cfg.OUamp =   0.05 # 0.00007 # 200 # 0.05
cfg.OUstd =   0.5 * cfg.OUamp# 35
cfg.NoiseConductanceDur = cfg.duration

# ------------------------------------------------------------------------------
# NetStim inputs
# ------------------------------------------------------------------------------
cfg.addNetStim = 0

cfg.tune = {}
cfg.update_cfg()
