from netpyne.batchtools import specs
import numpy as np

cfg = specs.SimConfig()

# ------------------------------------------------------------------------------
# Run parameters
# ------------------------------------------------------------------------------
cfg.duration = 7 * 1e3 # Duration of the sim, in ms
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
cfg.printPopAvgRates = [0, cfg.duration]
cfg.validateNetParams = False

cfg.seeds['stim'] = 1 
cfg.seeds['conn'] = 1

# ------------------------------------------------------------------------------
# Recording
# ------------------------------------------------------------------------------
POP_ACTIVE = 'IT5A'
cfg.pops_active = [POP_ACTIVE]
cfg.allpops = cfg.pops_active

# Choose the cells to record voltages for each active pop.
ncells_rec = 500
# this is a simplification, in the original code it's loaded from a file
pops_sz = {'IT5A': 500} 
cfg.pop_cells_rec = {}
for pop in cfg.allpops:
    N = np.minimum(pops_sz[pop], ncells_rec)
    cfg.pop_cells_rec[pop] = np.linspace(0, pops_sz[pop] - 1, N, dtype=int)

# Record voltage traces
cfg.recordCells = [(pop, list(cfg.pop_cells_rec[pop]))
                    for pop in cfg.allpops]
cfg.recordTraces = {
    'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}
}
cfg.recordStep =  0.1
cfg.recordStim = False
cfg.recordTime = True
cfg.recordLFP = False
cfg.recordDipole = False


# ------------------------------------------------------------------------------
# Saving
# ------------------------------------------------------------------------------
cfg.simLabel = 'sim_IT5A_kdr_mult_3_ramp_1.5_rx_75_wx_0.5_ouamp_-0.02_0.18'
cfg.saveFolder = 'sim_output/' + cfg.simLabel
cfg.savePickle = True
cfg.saveJson = False
cfg.saveDataInclude = ['simData', 'simConfig', 'net', 'netParams',  'netCells', 'netPops']
cfg.backupCfgFile = None
cfg.gatherOnlySimData = False
cfg.saveCellSecs = False
cfg.saveCellConns = False

# ------------------------------------------------------------------------------
# Analysis and plotting
# ------------------------------------------------------------------------------
cfg.analysis['plotRaster'] = {
    'include': cfg.pops_active,
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
cfg.AMPATau2Factor = 1.0

# ------------------------------------------------------------------------------
# Network
# ------------------------------------------------------------------------------
cfg.singleCellPops = False
cfg.reducedPop = False
cfg.singlePop = ''
cfg.removeWeightNorm = False
cfg.scale = 1.0
cfg.sizeY = 2000.0
cfg.sizeX = 100.0
cfg.sizeZ = 100.0
cfg.scaleDensity = 1.0

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
cfg.bkg_spike_inputs = {
    pop: {'r': cfg.bkg_r, 'w': cfg.bkg_w}
    for pop in cfg.pops_active
}

# Strong ramp-up pulse for switching between the steady-states
cfg.ou_ramp_dur = 1000   # duration
cfg.ou_ramp_t0 = 3500    # start time
cfg.ou_ramp_offset = 1.5   # amplitude (current to soma)
cfg.ou_ramp_mult = 0
cfg.ou_ramp_type = 'up'

# Mechanisms to modify
cfg.mech_changes = {
    'sec': 'all',
    'mech': 'kdr',
    'par': 'gbar',
    'mult': 3
}

# Update via batchtools
# this is not defined in this file, so we'll skip it
# if hasattr(cfg, 'update_cfg'):
#     cfg.update_cfg()

cfg.tune = {}