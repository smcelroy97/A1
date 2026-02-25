from netpyne.batchtools import specs
import numpy as np

cfg = specs.SimConfig()

# ------------------------------------------------------------------------------
# Run parameters
# ------------------------------------------------------------------------------
cfg.duration = 7 * 1e3  # Duration of the sim, in ms
cfg.dt = 0.05                  ## Internal Integration Time Step
cfg.verbose = False         	## Show detailed messages
cfg.hParams['celsius'] = 37
cfg.createNEURONObj = 1
cfg.createPyStruct = 1
cfg.printRunTime = 0.1

cfg.connRandomSecFromList = False  # set to false for reproducibility
cfg.cvode_active = False
cfg.cvode_atol = 1e-6
cfg.cache_efficient = True
cfg.oneSynPerNetcon = False
cfg.includeParamsLabel = False
#cfg.printPopAvgRates = [0, cfg.duration] # don't use cfg.duration as a reference structure...
cfg.validateNetParams = False

cfg.seeds['stim'] = 1
cfg.seeds['conn'] = 1

# ------------------------------------------------------------------------------
# Recording
# ------------------------------------------------------------------------------

# Populations to use
POP_ACTIVE = 'IT5A'
cfg.pops_active = [POP_ACTIVE]
cfg.allpops = cfg.pops_active
if 'plotRaster' in cfg.analysis:
    cfg.analysis['plotRaster']['include'] = cfg.pops_active
if 'plotSpikeStats' in cfg.analysis:
    cfg.analysis['plotSpikeStats']['include'] = cfg.pops_active
if 'plotTraces' in cfg.analysis:
    cfg.analysis['plotTraces']['include'] = cfg.pops_active

# original code ---
# 359 'IT5A' cells ---

# Record voltage traces
cfg.recordCells = [['IT5A', [*range(359)]]]
cfg.recordTraces = {
    'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}
}
cfg.recordStep = 0.1
cfg.recordStim = False
cfg.recordTime = True
cfg.recordLFP = False
cfg.recordDipole = False


# ------------------------------------------------------------------------------
# Saving
# ------------------------------------------------------------------------------
cfg.simLabel = 'basic_sim'
cfg.saveFolder = 'batch'
cfg.savePickle = True
cfg.saveJson = True
cfg.saveDataInclude = ['simData', 'simConfig', 'net', 'netParams',  'netCells', 'netPops']
cfg.backupCfgFile = None
cfg.gatherOnlySimData = False
cfg.saveCellSecs = False
cfg.saveCellConns = False

# ------------------------------------------------------------------------------
# Analysis and plotting
# ------------------------------------------------------------------------------
cfg.analysis['plotRaster'] = {
    'include': ['IT5A'],
    'saveFig': True,
    'showFig': False,
    'orderInverse': True,
    'figSize': (25, 25),
    'markerSize': 1
}

cfg.analysis['plotSpikeStats'] = False

# ------------------------------------------------------------------------------
# Cells
# ------------------------------------------------------------------------------
cfg.weightNormThreshold = 5.0
cfg.weightNormScaling = {'NGF_reduced': 1.0, 'ITS4_reduced': 1.0}
cfg.ihGbar = 1.0
cfg.KgbarFactor = 1.0

# ------------------------------------------------------------------------------
# Synapses
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Network
# ------------------------------------------------------------------------------
cfg.singleCellPops = False
cfg.reducedPop = False
cfg.singlePop = ''
cfg.removeWeightNorm = False

# ------------------------------------------------------------------------------
# Connectivity
# ------------------------------------------------------------------------------
cfg.addConn = 0
cfg.addSubConn = 1
cfg.wireCortex = 1
cfg.wmult = 1.0
cfg.addIntraThalamicConn = 1
cfg.addCorticoThalamicConn = 1
cfg.addThalamoCorticalConn = 1

# ------------------------------------------------------------------------------
# Background inputs
# ------------------------------------------------------------------------------
cfg.addBkgConn = 0
cfg.noiseBkg = 1.0
cfg.delayBkg = 5.0
cfg.startBkg = 0
cfg.rateBkg = {'exc': 40, 'inh': 40}
cfg.EbkgThalamicGain = 1.0
cfg.IbkgThalamicGain = 1.0

# ------------------------------------------------------------------------------
# Current inputs
# ------------------------------------------------------------------------------
cfg.addIClamp = False
cfg.addRIClamp = False

# ------------------------------------------------------------------------------
# OU current or conductance inputs
# -----------------------------------------------------------------------------
cfg.add_ou_current = 1
cfg.add_ou_conductance = 0
cfg.ou_common = 1
cfg.ou_tau = 10
cfg.ou_noise_duration = cfg.duration
cfg.OUamp = [-0.02, 0.18]
cfg.OUstd = 0

# ------------------------------------------------------------------------------
# NetStim inputs
# ------------------------------------------------------------------------------
cfg.addNetStim = False

# NetStim inputs (weak, just to randomly jitter the cells between steady-states)
cfg.bkg_r = 75    # firing rate
cfg.bkg_w = 0.5   # weight

# Strong ramp-up pulse for switching between the steady-states
cfg.ou_ramp_dur = 1000   # duration
cfg.ou_ramp_t0 = 3500    # start time
cfg.ou_ramp_offset = 1.5   # amplitude (current to soma)
cfg.ou_ramp_mult = 0
cfg.ou_ramp_type = 'up'

cfg.batch_id = 0 # assist labelling

# Mechanisms to modify...
# see in netParams.py multiply_parameters_func ...
# def multiply_parameters_func(pop: str,
#                              secs: list,
#                              mech: str,
#                              parameter: str,
#                              factor: int|float):
# 'kdr0' and 'cal0', labels, dictionary of 'secs', 'mech', 'parameter', 'factor' form the kwargs...

cfg.multiply_parameters = {
    'kdr0': {
        'secs': ('Adend1', 'Adend2', 'Adend3', 'Bdend', 'axon', 'soma'),
        'mech': 'kdr',
        'parameter': 'gbar',
        'factor': 1,
    }
}

cfg.update()
