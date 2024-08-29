"""
cfg.py

Simulation configuration for A1 model (using NetPyNE)
This file has sim configs as well as specification for parameterized values in netParams.py

Contributors: ericaygriffith@gmail.com, salvadordura@gmail.com, samnemo@gmail.com
"""

from netpyne import specs
import pickle

from netpyne.specs import SimConfig

cfg: SimConfig = specs.SimConfig()

# ------------------------------------------------------------------------------
#
# SIMULATION CONFIGURATION
#
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Run parameters
# ------------------------------------------------------------------------------
cfg.duration = 6500  # Duration of the sim, in ms
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
               'IRE', 'IREM', 'TI', 'TIM', 'IC', 'cochlea']
cfg.allCorticalPops = ['NGF1', 'IT2', 'SOM2', 'PV2', 'VIP2', 'NGF2', 'IT3', 'SOM3', 'PV3', 'VIP3', 'NGF3', 'ITP4',
                       'ITS4', 'SOM4', 'PV4', 'VIP4', 'NGF4', 'IT5A', 'CT5A', 'SOM5A', 'PV5A', 'VIP5A', 'NGF5A', 'IT5B',
                       'PT5B', 'CT5B', 'SOM5B', 'PV5B', 'VIP5B', 'NGF5B', 'IT6', 'CT6', 'SOM6', 'PV6', 'VIP6', 'NGF6']
cfg.allThalPops = ['TC', 'TCM', 'HTC', 'IRE', 'IREM', 'TI', 'TIM', 'IC']

cfg.thalInhib = ['IRE', 'IREM', 'TI', 'TIM']

alltypes = ['NGF1', 'IT2', 'PV2', 'SOM2', 'VIP2', 'ITS4', 'PT5B', 'TC', 'HTC', 'IRE', 'TI']

# Dict with traces to record -- taken from M1 cfg.py
cfg.recordTraces = {'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}}
cfg.recordStim = False  # Seen in M1 cfg.py
cfg.recordTime = True  # SEen in M1 cfg.py
cfg.recordStep = 0.05  # Step size (in ms) to save data -- value from M1 cfg.py


cfg.recordLFP = [[100, y, 100] for y in range(0, 2000, 100)]
# cfg.recordLFP = [[x, 1000, 100] for x in range(100, 2200, 200)] #+[[100, 2500, 200], [100,2700,200]]
# cfg.saveLFPPops =  cfg.allpops #, "IT3", "SOM3", "PV3", "VIP3", "NGF3", "ITP4",
# "ITS4", "IT5A", "CT5A", "IT5B", "PT5B", "CT5B", "IT6", "CT6"]

cfg.recordDipole = False
# cfg.saveDipoleCells = ['all']
# cfg.saveDipolePops = cfg.allpops

# ------------------------------------------------------------------------------
# Saving
# ------------------------------------------------------------------------------

cfg.simLabel = 'newBatchTest0815'
cfg.saveFolder = 'data/' + cfg.simLabel  # Set file output name
cfg.savePickle = True  # Save pkl file
cfg.saveJson = False  # Save json file
cfg.saveDataInclude = ['simData', 'simConfig', 'net']
cfg.backupCfgFile = None
cfg.gatherOnlySimData = False
cfg.saveCellSecs = False
cfg.saveCellConns = False

# ------------------------------------------------------------------------------
# Analysis and plotting
# ------------------------------------------------------------------------------

# cfg.analysis['plotTraces'] = {'include': [('TC', i) for i in range(40)], 'timeRange': [0, cfg.duration],
# 'oneFigPer': 'trace', 'overlay': True, 'saveFig': True, 'showFig': False, 'figSize':(12,8)}
# #[(pop,0) for pop in alltypes]		## Seen in M1 cfg.py (line 68)
# cfg.analysis['plotTraces'] = {'include': ['TC', 'IRE'],  'timeRange': [0, cfg.duration], 'oneFigPer': 'trace',
# 'overlay': True, 'saveFig': True, 'showFig': False, 'figSize':(12,8)} #[(pop,0) for pop in alltypes]
cfg.analysis['plotRaster'] = {'include': cfg.allpops, 'saveFig': True, 'showFig': False, 'orderInverse': True,
                              'timeRange': [0, cfg.duration], 'figSize': (25, 25), 'plotRates': False,
                              'markerSize': 1}   # Plot a raster
cfg.analysis['plotConn'] = {'includePre': [cfg.allThalPops, cfg.allCorticalPops],
                            'includePost': [cfg.allThalPops, cfg.allCorticalPops], 'saveFig': True}
# cfg.analysis['plotSpikeStats'] = {'stats': ['isicv', 'rate'], 'figSize': (6, 12), 'dpi': 300, 'saveFig': True}

# cfg.analysis['plotLFP'] = {'plots': ['timeSeries'], 'electrodes': [10], 'maxFreq': 80, 'figSize': (8,4),
# 'saveData': False, 'saveFig': True, 'showFig': False} # 'PSD', 'spectrogram'
# cfg.analysis['plotDipole'] = {'saveFig': True}
# cfg.analysis['plotEEG'] = {'saveFig': True}


layer_bounds = {'L1': 100, 'L2': 160, 'L3': 950, 'L4': 1250, 'L5A': 1334, 'L5B': 1550, 'L6': 2000}
# cfg.analysis['plotCSD'] = {'spacing_um': 100, 'LFP_overlay': 1, 'layer_lines': 1, 'layer_bounds': layer_bounds,
# 'saveFig': 1, 'showFig': 0}

# Plot 2D visualization of cell positions & connections
# cfg.analysis['plot2Dnet'] = {'include' : ['cochlea', cfg.allThalPops ], 'showConns': 1, 'saveFig': 1}


# ------------------------------------------------------------------------------
# Cells
# ------------------------------------------------------------------------------
cfg.weightNormThreshold = 5.0  # maximum weight normalization factor with respect to the soma
cfg.weightNormScaling = {'NGF_reduced': 1.0, 'ITS4_reduced': 1.0}
cfg.ihGbar = 1.0
cfg.KgbarFactor = 1.0
# For testing reduction in T-type calcium channel conductances
# cfg.tTypeCorticalFactor = 1.0
# cfg.tTypeThalamicFactor = 1.0
# For testing NMDAR manipulations:
# cfg.NMDARfactor = 1.0

# ------------------------------------------------------------------------------
# Synapses
# ------------------------------------------------------------------------------
cfg.AMPATau2Factor = 1.0
cfg.synWeightFractionEE = [0.5, 0.5]  # E->E AMPA to NMDA ratio
cfg.synWeightFractionEI = [0.5, 0.5]  # E->I AMPA to NMDA ratio
cfg.synWeightFractionIE = [0.9, 0.1]
cfg.synWeightFractionII = [1.0]
cfg.synWeightFractionEI_CustomCort = [0.5, 0.5]  # E->I AMPA to NMDA ratio custom for cortex NMDA manipulation
cfg.synWeightFractionSOME = [0.9, 0.2]  # SOM -> E GABAASlow to GABAB ratio
cfg.synWeightFractionSOMI = [0.9, 0.1]  # SOM -> I GABAASlow to GABAB ratio
cfg.synWeightFractionNGF = [0.5, 0.9]  # NGF GABAA to GABAB ratio
cfg.synWeightFractionNGFE = [0.5, 1.0]
cfg.synWeightFractionNGFI = [1.0]
cfg.synWeightFractionENGF = [0.834, 0.166]  # NGF AMPA to NMDA ratio
cfg.useHScale = False

cfg.synWeightFractionThalIE = [0.9, 0.2]
cfg.synWeightFractionThalII = [1.0, 0.0]
cfg.synWeightFractionThalCtxII = [1.0]
cfg.synWeightFractionThalCtxIE = [1.0, 0.0]
# ------------------------------------------------------------------------------
# Network
# ------------------------------------------------------------------------------
# These values taken from M1 cfg (https://github.com/Neurosim-lab/netpyne/blob/development/examples/M1detailed/cfg.py)
cfg.singleCellPops = False
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
cfg.addConn = 1.0
cfg.wireCortex = 1.0

# cfg.EEGain = 0.75
# cfg.EIGain = 1.5
# cfg.IEGain = 1.5
# cfg.IIGain = 1.0

cfg.EEGain = 1.1
cfg.EIGain = 1.6313576020869256
cfg.IEGain = 2.06
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
cfg.intraThalamicEIGain = 1.0
cfg.intraThalamicIEGain = 1.0
cfg.intraThalamicIIGain = 1.0

# these params control IC -> Thalamic Core
cfg.ICThalweightECore = 0.8350476447841453
cfg.ICThalweightICore = 0.2114492149101151
cfg.ICThalprobECore = 0.163484173596043
cfg.ICThalprobICore = 0.0936669688856933

# these params control IC -> Thalamic Matrix
cfg.ICThalMatrixCoreFactor = 0.1
cfg.ICThalprobEMatrix = cfg.ICThalprobECore
cfg.ICThalprobIMatrix = cfg.ICThalprobICore

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


# these params added from Christoph Metzner branch
# Control the strength of thalamic inputs to different subpopulations
cfg.thalL4PV = 0.21367245896786016
cfg.thalL4SOM = 0.24260966747847523
cfg.thalL4E = 2.0 #1.9540886147587417

cfg.thalL4VIP = 1.0
cfg.thalL4NGF = 1.0
cfg.L3L3scaleFactor = 1.0
cfg.CT6ScaleFactor = 1.0



cfg.thalL1NGF = 1.0
cfg.ENGF1 = 1.0

# Modulate strength of connections from L4 -> L3 by different target subpops
cfg.L4L3E = 1.0
cfg.L4L3PV = 1.0
cfg.L4L3SOM = 1.0

cfg.L4L3VIP = 1.0
cfg.L4L3NGF = 1.0

cfg.L4L4E = 1.0

# L3 -> L4 Inhib pops
cfg.L3L4PV = 1.0
cfg.L3L4SOM = 1.0

# Artificial Feedback Params
cfg.artFB = False
cfg.artFBweight = 20.0
cfg.artFBprob = 0.5

cfg.addSubConn = 1

cfg.alterSyn = 0
cfg.alterSyn2 = 0
cfg.alterSyn3 = 0

# full weight conn matrix
with open('conn/conn.pkl', 'rb') as fileObj:
    connData = pickle.load(fileObj)
cfg.wmat = connData['wmat']

cfg.seeds = {'conn': 23451, 'stim': 1, 'loc': 1}
# ------------------------------------------------------------------------------
# Background inputs
# ------------------------------------------------------------------------------
cfg.addBkgConn = 1
cfg.noiseBkg = 1.0  # firing rate random noise
cfg.delayBkg = 5.0  # (ms)
cfg.startBkg = 0  # start at 0 ms

# cfg.weightBkg = {'IT': 12.0, 'ITS4': 0.7, 'PT': 14.0, 'CT': 14.0,
#                 'PV': 28.0, 'SOM': 5.0, 'NGF': 80.0, 'VIP': 9.0,
#                 'TC': 1.8, 'HTC': 1.55, 'RE': 9.0, 'TI': 3.6}
cfg.rateBkg = {'exc': 40, 'inh': 40}

# options to provide external sensory input
# cfg.randomThalInput = True  # provide random bkg inputs spikes (NetStim) to thalamic populations

cfg.EbkgThalamicGain = 0.392
cfg.IbkgThalamicGain = 1.96

cfg.NGF6bkgGain = 1.0

cfg.cochlearThalInput = True
# parameters to generate realistic  auditory thalamic inputs using Brian Hears


if cfg.cochlearThalInput:
    cfg.cochlearThalInput = {"lonset" : [0], "numCenterFreqs": 100, "freqRange":[125, 20000], "loudnessScale": 1,
                             "lfnwave": ["wav/silence6s.wav"]}
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
cfg.addIClamp = 0

# ------------------------------------------------------------------------------
# NetStim inputs
# ------------------------------------------------------------------------------

cfg.addNetStim = 0

cfg.tune = {}
# # ------------------------ ADD PARAM VALUES FROM .JSON FILES:
# # COMMENT THIS OUT IF USING GCP !!! ONLY USE IF USING NEUROSIM!!!
# import json
#
# with open('data/v34_batch25/trial_2142/trial_2142_cfg.json',
#           'rb') as f:  # 'data/salva_runs/v29_batch3_trial_13425_cfg.json'
#     cfgLoad = json.load(f)['simConfig']
#
# ## UPDATE CORTICAL GAIN PARAMS
# cfg.EEGain = cfgLoad['EEGain']
# cfg.EIGain = cfgLoad['EIGain']
# cfg.IEGain = cfgLoad['IEGain']
# cfg.IIGain = cfgLoad['IIGain']
#
# cfg.EICellTypeGain['PV'] = cfgLoad['EICellTypeGain']['PV']
# cfg.EICellTypeGain['SOM'] = cfgLoad['EICellTypeGain']['SOM']
# cfg.EICellTypeGain['VIP'] = cfgLoad['EICellTypeGain']['VIP']
# cfg.EICellTypeGain['NGF'] = cfgLoad['EICellTypeGain']['NGF']
#
# cfg.IECellTypeGain['PV'] = cfgLoad['IECellTypeGain']['PV']
# cfg.IECellTypeGain['SOM'] = cfgLoad['IECellTypeGain']['SOM']
# cfg.IECellTypeGain['VIP'] = cfgLoad['IECellTypeGain']['VIP']
# cfg.IECellTypeGain['NGF'] = cfgLoad['IECellTypeGain']['NGF']
#
# cfg.EILayerGain['1'] = cfgLoad['EILayerGain']['1']
# cfg.IILayerGain['1'] = cfgLoad['IILayerGain']['1']
#
# cfg.EELayerGain['2'] = cfgLoad['EELayerGain']['2']
# cfg.EILayerGain['2'] = cfgLoad['EILayerGain']['2']
# cfg.IELayerGain['2'] = cfgLoad['IELayerGain']['2']
# cfg.IILayerGain['2'] = cfgLoad['IILayerGain']['2']
#
# cfg.EELayerGain['3'] = cfgLoad['EELayerGain']['3']
# cfg.EILayerGain['3'] = cfgLoad['EILayerGain']['3']
# cfg.IELayerGain['3'] = cfgLoad['IELayerGain']['3']
# cfg.IILayerGain['3'] = cfgLoad['IILayerGain']['3']
#
# cfg.EELayerGain['4'] = cfgLoad['EELayerGain']['4']
# cfg.EILayerGain['4'] = cfgLoad['EILayerGain']['4']
# cfg.IELayerGain['4'] = cfgLoad['IELayerGain']['4']
# cfg.IILayerGain['4'] = cfgLoad['IILayerGain']['4']
#
# cfg.EELayerGain['5A'] = cfgLoad['EELayerGain']['5A']
# cfg.EILayerGain['5A'] = cfgLoad['EILayerGain']['5A']
# cfg.IELayerGain['5A'] = cfgLoad['IELayerGain']['5A']
# cfg.IILayerGain['5A'] = cfgLoad['IILayerGain']['5A']
#
# cfg.EELayerGain['5B'] = cfgLoad['EELayerGain']['5B']
# cfg.EILayerGain['5B'] = cfgLoad['EILayerGain']['5B']
# cfg.IELayerGain['5B'] = cfgLoad['IELayerGain']['5B']
# cfg.IILayerGain['5B'] = cfgLoad['IILayerGain']['5B']
#
# cfg.EELayerGain['6'] = cfgLoad['EELayerGain']['6']
# cfg.EILayerGain['6'] = cfgLoad['EILayerGain']['6']
# cfg.IELayerGain['6'] = cfgLoad['IELayerGain']['6']
# cfg.IILayerGain['6'] = cfgLoad['IILayerGain']['6']
#
# # UPDATE THALAMIC GAIN PARAMS
# cfg.thalamoCorticalGain = cfgLoad['thalamoCorticalGain']
# cfg.intraThalamicGain = cfgLoad['intraThalamicGain']
# cfg.EbkgThalamicGain = cfgLoad['EbkgThalamicGain']
# cfg.IbkgThalamicGain = cfgLoad['IbkgThalamicGain']
#
# # UPDATE WMAT VALUES
# cfg.wmat = cfgLoad['wmat']

cfg.ICThalInput = False
# cfg.ICThalInput = {'file': 'data/ICoutput/40Hz_10kHz_4s_AM_click_train_1kBMF_100CF.mat',
#                    'startTime': 3000,  # list(np.arange(4000, 8000, 300)),
#                    'weightECore': cfg.ICThalweightECore,
#                    'weightICore': cfg.ICThalweightICore,
#                    'probECore': cfg.ICThalprobECore,
#                    'probICore': cfg.ICThalprobICore,
#                    'probEMatrix': cfg.ICThalprobEMatrix,
#                    'probIMatrix': cfg.ICThalprobIMatrix,
#                    'MatrixCoreFactor': cfg.ICThalMatrixCoreFactor,
#                    'seed': 1}  # SHOULD THIS BE ZERO?
#
# cfg.artFB = {'file': 'data/FBinput/FBinput_test_numCell200.pkl',
#              'weight': cfg.artFBweight,
#              'prob': cfg.artFBprob,
#              }
