import pickle
import json
import numpy as np

from netpyne.batchtools import specs

cfg = specs.SimConfig()

# Read the default config
with open('data/cfg_base.json', 'r') as fid:
    dconf = json.load(fid)

# ------------------------------------------------------------------------------
# Run parameters
# ------------------------------------------------------------------------------
cfg.duration = dconf['sim']['duration']  # Duration of the sim, in ms
cfg.dt = dconf['sim']['dt']  ## Internal Integration Time Step
cfg.verbose = dconf['verbose']  ## Show detailed messages
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

cfg.seeds['stim'] = dconf['net']['stimseed']  # stimulation random number generator seed
cfg.seeds['conn'] = dconf['net']['connseed']  # connectivity random number generator seed

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

cfg.Epops = ['IT2', 'IT3', 'ITP4', 'ITS4', 'IT5A', 'CT5A', 'IT5B', 'CT5B', 'PT5B', 'IT6', 'CT6']  # all layers
cfg.Ipops = [
    'NGF1',  # L1
    'PV2', 'SOM2', 'VIP2', 'NGF2',  # L2
    'PV3', 'SOM3', 'VIP3', 'NGF3',  # L3
    'PV4', 'SOM4', 'VIP4', 'NGF4',  # L4
    'PV5A', 'SOM5A', 'VIP5A', 'NGF5A',  # L5A
    'PV5B', 'SOM5B', 'VIP5B', 'NGF5B',  # L5B
    'PV6', 'SOM6', 'VIP6', 'NGF6'  # L6
]

cfg.TEpops = ['TC', 'TCM', 'HTC']
cfg.TIpops = ['IRE', 'IREM', 'TI', 'TIM']

# Dict with traces to record -- taken from M1 cfg.py
cfg.recordTraces = {
    # 'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}
    # 'g_NMDA': {'sec':'soma', 'loc':0.5, 'synMech':'NMDA', 'var':'g'},
    # 'g_GABAB': {'sec':'soma', 'loc':0.5, 'synMech':'GABAB', 'var':'g'}
}
cfg.recordStim = False  # Seen in M1 cfg.py
cfg.recordTime = True  # SEen in M1 cfg.py
cfg.recordStep = 0.05  # St ep size (in ms) to save data -- value from M1 cfg.py

cfg.recordLFP = False  # [[100, y, 100] for y in range(0, 2000, 100)]
cfg.recordDipole = False

# ------------------------------------------------------------------------------
# Saving
# ------------------------------------------------------------------------------

cfg.simLabel = 'SIM_LABEL_DEFAULT'  # will be set in exp_cfg.py
cfg.saveFolder = 'simOutput/' + cfg.simLabel  # Set file output name
cfg.savePickle = True  # Save pkl file
cfg.saveJson = False  # Save json file
cfg.saveDataInclude = ['simData', 'simConfig', 'net', 'netParams']
cfg.backupCfgFile = True
cfg.gatherOnlySimData = False
cfg.saveCellSecs = False
cfg.saveCellConns = False

# ------------------------------------------------------------------------------
# Analysis and plotting
# ------------------------------------------------------------------------------

cfg.analysis['plotRaster'] = {
    'include': cfg.allpops,
    'saveFig': True,
    'showFig': False,
    'orderInverse': True,
    'figSize': (25, 25),
    'markerSize': 1
}

cfg.analysis['plotSpikeStats'] = {
    'include': cfg.allpops,
    'stats': ['rate', 'isicv'],
    'figSize': (6, 12),
    'timeRange': [1000, cfg.duration],
    'dpi': 300,
    'showFig': 0,
    'saveFig': 1
}


# cfg.analysis['plotTraces'] = {'include': cfg.allpops, 'timeRange': [0, cfg.duration],
# 'oneFigPer': 'cell', 'overlay': True, 'saveFig': False, 'showFig': False, 'figSize':(12,8)}

def setplotTraces(ncell=50, linclude=cfg.allpops, timeRange=cfg.duration):
    pops = []
    for pop in linclude:
        for i in range(ncell):
            pops.append((pop, i))
    cfg.analysis['plotTraces'] = {'include': linclude, 'timeRange': timeRange, 'oneFigPer': 'trace', 'overlay': True, 'saveFig': False, 'showFig': False, 'figSize': (12, 8)}


# setplotTraces(ncell=1, timeRange=[1750, 3000])

layer_bounds = {'L1': 100, 'L2': 160, 'L3': 950, 'L4': 1250, 'L5A': 1334, 'L5B': 1550, 'L6': 2000}

# ------------------------------------------------------------------------------
# Cells
# ------------------------------------------------------------------------------

cfg.weightNormThreshold = 5.0  # maximum weight normalization factor with respect to the soma
cfg.weightNormScaling = {'NGF_reduced': 1.0, 'ITS4_reduced': 1.0}
cfg.ihGbar = 1.0
cfg.KgbarFactor = 1.0

# ------------------------------------------------------------------------------
# Synapses
# ------------------------------------------------------------------------------

cfg.AMPATau2Factor = 1.0
cfg.useHScale = False

cfg.synWeightFractionEE = dconf['syn']['synWeightFractionEE']  # [0.5, 0.5] # E->E AMPA to NMDA ratio
cfg.synWeightFractionEI = dconf['syn']['synWeightFractionEI']  # [0.5, 0.5] # E->I AMPA to NMDA ratio
cfg.synWeightFractionEI_CustomCort = dconf['syn']['synWeightFractionEI_CustomCort']  # [0.5, 0.5] # E->I AMPA to NMDA ratio custom for cortex NMDA manipulation
cfg.synWeightFractionIE = dconf['syn']['synWeightFractionIE']  # [1.0] # this is set to 1 for PV,VIP; for SOM,NGF have other param for GABAASlow to GABAB ratio
cfg.synWeightFractionII = dconf['syn']['synWeightFractionII']  # [1.0]  # I->I uses single synapse mechanism

cfg.synWeightFractionNGF = dconf['syn']['synWeightFractionNGF']  # {'E':[0.5, 0.5],'I':[0.9,0.1]} # NGF GABAA to GABAB ratio when connecting to E , I neurons
cfg.synWeightFractionSOM = dconf['syn']['synWeightFractionSOM']  # {'E':[0.9, 0.1],'I':[0.9,0.1]} # SOM GABAA to GABAB ratio when connection to E , I neurons
cfg.synWeightFractionENGF = dconf['syn']['synWeightFractionENGF']  # [0.834, 0.166] # AMPA to NMDA ratio for E -> NGF connections

cfg.synWeightFractionThal = dconf['syn']['synWeightFractionThal']

cfg.GABABThal = dconf['syn']['GABABThal']
cfg.GABABCtx = dconf['syn']['GABABCtx']

# ------------------------------------------------------------------------------
# Network
# ------------------------------------------------------------------------------

# These values taken from M1 cfg (https://github.com/Neurosim-lab/netpyne/blob/development/examples/M1detailed/cfg.py)
cfg.singleCellPops = False
cfg.reducedPop = False  # insert number to declare specific number of populations, if going for full model set to False
cfg.singlePop = ''
cfg.removeWeightNorm = False

cfg.scale = dconf['net']['scale']
cfg.sizeY = dconf['net']['sizeY']
cfg.sizeX = dconf['net']['sizeX']
cfg.sizeZ = dconf['net']['sizeZ']
cfg.scaleDensity = dconf['net']['scaleDensity']

# ------------------------------------------------------------------------------
# Connectivity
# ------------------------------------------------------------------------------

# Cortical
cfg.addConn = 1
cfg.addSubConn = 1
cfg.wireCortex = 1

# Global weight multiplier
cfg.wmult = 1.0

# Thalamic flags
cfg.addIntraThalamicConn = dconf['net']['addIntraThalamicConn']
cfg.addCorticoThalamicConn = dconf['net']['addCorticoThalamicConn']
cfg.addThalamoCorticalConn = dconf['net']['addThalamoCorticalConn']


# Gains
def set_gains():
    cfg.EEGain = dconf['net']['EEGain']
    cfg.EIGain = dconf['net']['EIGain']
    cfg.IEGain = dconf['net']['IEGain']
    cfg.IIGain = dconf['net']['IIGain']

    cfg.EICellTypeGain = dconf['net']['EICellTypeGain']
    cfg.IECellTypeGain = dconf['net']['IECellTypeGain']

    cfg.EEPopGain = dconf['net']['EEPopGain']
    cfg.EIPopGain = dconf['net']['EIPopGain']

    cfg.EELayerGain = dconf['net']['EELayerGain']
    cfg.EILayerGain = dconf['net']['EILayerGain']
    cfg.IELayerGain = dconf['net']['IELayerGain']
    cfg.IILayerGain = dconf['net']['IILayerGain']

    cfg.intraThalamicGain = dconf['net']['intraThalamicGain']
    cfg.corticoThalamicGain = dconf['net']['corticoThalamicGain']
    cfg.thalamoCorticalGain = dconf['net']['thalamoCorticalGain']

    # these params added from Christoph Metzner branch
    # these control strength of thalamic inputs to different subpopulations
    cfg.thalL4PV = dconf['net']['thalL4PV']
    cfg.thalL4SOM = dconf['net']['thalL4SOM']
    cfg.thalL4E = dconf['net']['thalL4E']
    cfg.thalL4VIP = dconf['net']['thalL4VIP']
    cfg.thalL4NGF = dconf['net']['thalL4NGF']
    cfg.thalL1NGF = dconf['net']['thalL1NGF']
    cfg.ENGF1 = dconf['net']['ENGF1']

    # modulates strength of connections from L4 -> L3 by different target subpopulations
    # these next 5 param values are from after generation 59 of optunaERP_24mar5_ (optimized L3 sink)
    cfg.L4L3E = dconf['net']['L4L3E']
    cfg.L4L3PV = dconf['net']['L4L3PV']
    cfg.L4L3SOM = dconf['net']['L4L3SOM']
    cfg.L4L3VIP = dconf['net']['L4L3VIP']
    cfg.L4L3NGF = dconf['net']['L4L3NGF']

    cfg.intraThalamicCoreEEGain = dconf['net']['intraThalamicCoreEEGain']
    cfg.intraThalamicCoreEIGain = dconf['net']['intraThalamicCoreEIGain']
    cfg.intraThalamicCoreIEGain = dconf['net']['intraThalamicCoreIEGain']
    cfg.intraThalamicCoreIIGain = dconf['net']['intraThalamicCoreIIGain']
    cfg.intraThalamicEEGain = dconf['net']['intraThalamicEEGain']
    cfg.intraThalamicEIGain = dconf['net']['intraThalamicEIGain']
    cfg.intraThalamicIEGain = dconf['net']['intraThalamicIEGain']
    cfg.intraThalamicIIGain = dconf['net']['intraThalamicIIGain']


set_gains()


# IC -> Thalamus
def set_ic_thal_cfg():
    # IC -> Thalamic Core
    cfg.ICThalweightECore = dconf['net']['ICThalweightECore']
    cfg.ICThalweightICore = dconf['net']['ICThalweightICore']
    cfg.ICThalprobECore = dconf['net']['ICThalprobECore']
    cfg.ICThalprobICore = dconf['net']['ICThalprobICore']

    # IC -> Thalamic Matrix
    cfg.ICThalMatrixCoreFactor = dconf['net']['ICThalMatrixCoreFactor']
    cfg.ICThalprobEMatrix = cfg.ICThalprobECore
    cfg.ICThalprobIMatrix = cfg.ICThalprobICore

    cfg.ICThalInput = False
    if dconf['sim']['useICThal']:
        cfg.ICThalInput = {
            'file': dconf['ICThalInput']['file'],  # BBN_trials/ICoutput_CF_9600_10400_wav_BBN_100ms_burst_AN.mat',
            'startTime': list(np.arange(dconf['ICThalInput']['onset'],
                                        dconf['ICThalInput']['offset'],
                                        dconf['ICThalInput']['interval'])),
            'weightECore': cfg.ICThalweightECore,
            'weightICore': cfg.ICThalweightICore,
            'probECore': cfg.ICThalprobECore,
            'probICore': cfg.ICThalprobICore,
            'probEMatrix': cfg.ICThalprobEMatrix,
            'probIMatrix': cfg.ICThalprobIMatrix,
            'MatrixCoreFactor': cfg.ICThalMatrixCoreFactor,
            'seed': 1  # SHOULD THIS BE ZERO?
        }


set_ic_thal_cfg()


# Cochlea -> Thalamus
def set_coch_thal_cfg():
    cfg.cochThalweightECore = dconf['net']['cochThalweightECore']
    cfg.cochThalweightICore = dconf['net']['cochThalweightICore']
    cfg.cochThalweightEMatrix = dconf['net']['cochThalweightEMatrix']
    cfg.cochThalweightIMatrix = dconf['net']['cochThalweightIMatrix']
    cfg.cochThalprobECore = dconf['net']['cochThalprobECore']
    cfg.cochThalprobICore = dconf['net']['cochThalprobICore']
    cfg.cochThalprobEMatrix = dconf['net']['cochThalprobEMatrix']
    cfg.cochThalprobIMatrix = dconf['net']['cochThalprobIMatrix']
    cfg.cochThalFreqRange = dconf['net']['cochThalFreqRange']

    cfg.cochlearThalInput = False
    if dconf['sim']['useCochleaThal']:
        cfg.cochlearThalInput = dconf['CochlearThalInput']
        cti = cfg.cochlearThalInput
        cti['probECore'] = cfg.cochThalprobECore
        cti['weightECore'] = cfg.cochThalweightECore
        cti['probICore'] = cfg.cochThalprobICore
        cti['weightICore'] = cfg.cochThalweightICore
        cti['probEMatrix'] = cfg.cochThalprobEMatrix
        cti['weightEMatrix'] = cfg.cochThalweightEMatrix
        cti['probIMatrix'] = cfg.cochThalprobIMatrix
        cti['weightIMatrix'] = cfg.cochThalweightIMatrix


set_coch_thal_cfg()

# Thalamic core conn prob length constant
cfg.ThalamicCoreLambda = dconf['net']['ThalamicCoreLambda']

# Full weight conn matrix
with open('conn/conn.pkl', 'rb') as fileObj:
    connData = pickle.load(fileObj)
cfg.wmat = connData['wmat']

# ------------------------------------------------------------------------------
# Background inputs
# ------------------------------------------------------------------------------
cfg.addBkgConn = 0
cfg.noiseBkg = 1.0  # firing rate random noise
cfg.delayBkg = 5.0  # (ms)
cfg.startBkg = 0  # start at 0 ms
cfg.rateBkg = {'exc': 40, 'inh': 40}

cfg.EbkgThalamicGain = dconf['EbkgThalamicGain']
cfg.IbkgThalamicGain = dconf['IbkgThalamicGain']

# ------------------------------------------------------------------------------
# Current inputs
# ------------------------------------------------------------------------------

cfg.addIClamp = dconf['addIClamp']  # whether to apply current clamp
if cfg.addIClamp:
    cfg.IClamp = dconf['IClamp']

cfg.addRIClamp = dconf['addRIClamp']
if cfg.addRIClamp:
    cfg.RIClamp = dconf['RIClamp']


# ------------------------------------------------------------------------------
# OU current or conductance inputs
# -----------------------------------------------------------------------------
def set_ou_cfg():
    # Turn on current ot condactance OU inputs
    cfg.add_ou_current = 0
    cfg.add_ou_conductance = 0

    # Commonn OU for all pops or individual for each pop
    cfg.ou_common = 0

    # OU time constant
    cfg.ou_tau = 10

    # OU signal duration
    cfg.ou_noise_duration = cfg.duration
    # cfg.NoiseConductanceDur = cfg.duration   # for compatibility with previous version

    # Common OU properties
    cfg.OUamp = 1.0
    cfg.OUstd = 0.4 * cfg.OUamp

    # Individual OU properties for each population
    cfg.ou_pop_inputs = {}
    cfg.ou_params_fpath = ''


set_ou_cfg()

# ------------------------------------------------------------------------------
# NetStim inputs
# ------------------------------------------------------------------------------
cfg.addNetStim = dconf['addNetStim']  # whether to add additional external stimuli (not background stimuli)
if dconf['addNetStim']:
    for pop, dns in dconf['NetStim'].items():
        cfg.__dict__['NetStim' + pop + '_r'] = {
            'pop': pop, 'ynorm': [0, 1], 'sec': dns['sec'], 'loc': dns['loc'],
            'synMech': dns['synMech'], 'synMechWeightFactor': [1.0], 'start': dns['start'],
            'interval': dns['interval'], 'noise': dns['noise'], 'number': dns['number'],
            'weight': dns['weight'], 'delay': dns['delay']
        }
cfg.tune = {}