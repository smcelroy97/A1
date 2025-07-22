
#------------------------------------------------------------------------------
# Connectivity
#------------------------------------------------------------------------------
#cfg.synWeightFractionEE = [0.5, 0.5] # E->E AMPA to NMDA ratio
#cfg.synWeightFractionEI = [0.5, 0.5] # E->I AMPA to NMDA ratio
cfg.synWeightFractionIE = dconf['syn']['synWeightFractionIE'] # [1.0] # this is set to 1 for PV,VIP; for SOM,NGF have other param for GABAASlow to GABAB ratio
cfg.synWeightFractionII = dconf['syn']['synWeightFractionII'] # [1.0]  # I->I uses single synapse mechanism

# Cortical
cfg.addConn = 1


## E/I->E/I layer weights (L1-3, L4, L5, L6)
cfg.EELayerGain = {'1': 1.0, '2': 1.0, '3': 1.0, '4': 1.0 , '5A': 1.0, '5B': 1.0, '6': 1.0}
cfg.EILayerGain = {'1': 1.0, '2': 1.0, '3': 1.0, '4': 1.0 , '5A': 1.0, '5B': 1.0, '6': 1.0}
cfg.IELayerGain = {'1': 1.0, '2': 1.0, '3': 1.0, '4': 1.0 , '5A': 1.0, '5B': 1.0, '6': 1.0}
cfg.IILayerGain = {'1': 1.0, '2': 1.0, '3': 1.0, '4': 1.0 , '5A': 1.0, '5B': 1.0, '6': 1.0}

# E -> E based on postsynaptic cortical E neuron population
# cfg.EEPopGain = {'IT2': 1.3125, 'IT3': 1.55, 'ITP4': 1.0, 'ITS4': 1.0, 'IT5A': 1.05, 'CT5A': 1.1500000000000001, 'IT5B': 0.425, 'CT5B': 1.1500000000000001, 'PT5B': 1.05, 'IT6': 1.05, 'CT6': 1.05} # this is from after generation 203 of optunaERP_23dec23_ , values used in generation 204 of the same optimization
#cfg.EEPopGain = {'IT2': 1.4125, 'IT3': 3.0, 'ITP4': 1.0, 'ITS4': 1.05, 'IT5A': 1.1500000000000001, 'CT5A': 1.6500000000000006, 'IT5B': 0.6250000000000001, 'CT5B': 3.0, 'PT5B': 3.0, 'IT6': 1.4500000000000004, 'CT6': 1.2000000000000002} # this is from after generation 59 of optunaERP_24mar5_ (optimized L3 sink)
cfg.EEPopGain = dconf['net']['EEPopGain']

# gains from E -> I based on postsynaptic cortical I neuron population
# cfg.EIPopGain = {'NGF1': 1.0, 'SOM2': 1.0, 'PV2': 1.0, 'VIP2': 1.0, 'NGF2': 1.0, 'SOM3': 1.0, 'PV3': 1.0, 'VIP3': 1.0, 'NGF3': 1.0, 'SOM4': 1.0, 'PV4': 1.0, 'VIP4': 1.0, 'NGF4': 1.0, 'SOM5A': 1.0, 'PV5A': 1.4, 'VIP5A': 1.25, 'NGF5A': 0.8, 'SOM5B': 1.0, 'PV5B': 1.4, 'VIP5B': 1.4, 'NGF5B': 0.9, 'SOM6': 1.0, 'PV6': 1.4, 'VIP6': 1.4, 'NGF6': 0.65}
# cfg.EIPopGain = {'NGF1': 1.0, 'SOM2': 1.0, 'PV2': 1.0, 'VIP2': 1.0, 'NGF2': 1.0, 'SOM3': 1.0, 'PV3': 1.0, 'VIP3': 1.0, 'NGF3': 1.0, 'SOM4': 1.0, 'PV4': 1.0, 'VIP4': 1.0, 'NGF4': 1.0, 'SOM5A': 1.0, 'PV5A': 1.4, 'VIP5A': 1.25, 'NGF5A': 0.8, 'SOM5B': 1.0, 'PV5B': 1.45, 'VIP5B': 1.4, 'NGF5B': 0.9500000000000001, 'SOM6': 1.0, 'PV6': 1.4, 'VIP6': 1.3499999999999999, 'NGF6': 0.65} # this is from after generation 203 of optunaERP_23dec23_ , values used in generation 204 of the same optimization
#cfg.EIPopGain = {'NGF1': 1.2500000000000002, 'SOM2': 0.5999999999999996, 'PV2': 0.25, 'VIP2': 1.0, 'NGF2': 1.0, 'SOM3': 3.0, 'PV3': 1.0, 'VIP3': 1.0, 'NGF3': 1.0, 'SOM4': 1.0, 'PV4': 1.1, 'VIP4': 1.0, 'NGF4': 1.0, 'SOM5A': 1.0, 'PV5A': 1.8000000000000003, 'VIP5A': 1.35, 'NGF5A': 0.9500000000000002, 'SOM5B': 1.0, 'PV5B': 3.0, 'VIP5B': 1.5, 'NGF5B': 1.4500000000000004, 'SOM6': 0.95, 'PV6': 3.0, 'VIP6': 3.0, 'NGF6': 0.25} # this is from after generation 59 of optunaERP_24mar5_ (optimized L3 sink)
cfg.EIPopGain = dconf['net']['EIPopGain']

## E->I by target cell type
cfg.EICellTypeGain = {'PV': 1.0, 'SOM': 1.0, 'VIP': 1.0, 'NGF': 1.0}

## I->E by target cell type
cfg.IECellTypeGain = {'PV': 1.0, 'SOM': 1.0, 'VIP': 1.0, 'NGF': 1.0}

# Thalamic
cfg.addIntraThalamicConn = dconf['net']['addIntraThalamicConn']
cfg.addCorticoThalamicConn = dconf['net']['addCorticoThalamicConn']
cfg.addThalamoCorticalConn = dconf['net']['addThalamoCorticalConn']

cfg.corticoThalamicGain = dconf['net']['corticoThalamicGain']

# these params control IC -> Thalamic Core
cfg.ICThalweightECore = dconf['net']['ICThalweightECore'] # 0.8350476447841453 # 1.0218574230414905 # 1.1366391725804097  # 0.8350476447841453 # 1.0
cfg.ICThalweightICore = dconf['net']['ICThalweightICore'] # 0.2114492149101151 # 0.20065170901643178 # 0.21503725192597786 # 0.2114492149101151 # 0.25
cfg.ICThalprobECore = dconf['net']['ICThalprobECore'] # 0.163484173596043 # 0.17524000437877066 # 0.21638972066571394   # 0.163484173596043 # 0.19
cfg.ICThalprobICore = dconf['net']['ICThalprobICore'] # 0.0936669688856933 # 0.0978864963550709 # 0.11831534696879886   # 0.0936669688856933 # 0.12
# these params control IC -> Thalamic Matrix
cfg.ICThalMatrixCoreFactor = dconf['net']['ICThalMatrixCoreFactor'] # 0.1 # 0.0988423213016316 # 0.11412487872986073 # 0.1 # this is used to scale weights to thalamic matrix neurons in netParams.py
cfg.ICThalprobEMatrix = cfg.ICThalprobECore 
cfg.ICThalprobIMatrix = cfg.ICThalprobICore

# these params control cochlea -> Thalamus
cfg.cochThalweightECore = dconf['net']['cochThalweightECore'] # 0.4
cfg.cochThalweightICore = dconf['net']['cochThalweightICore'] # 0.1
cfg.cochThalweightEMatrix = dconf['net']['cochThalweightEMatrix'] # 0.4
cfg.cochThalweightIMatrix = dconf['net']['cochThalweightIMatrix'] # 0.1
cfg.cochThalprobECore = dconf['net']['cochThalprobECore'] # 0.16
cfg.cochThalprobICore = dconf['net']['cochThalprobICore'] # 0.09
cfg.cochThalprobEMatrix = dconf['net']['cochThalprobEMatrix'] # 0.16
cfg.cochThalprobIMatrix = dconf['net']['cochThalprobIMatrix'] # 0.09
cfg.cochThalFreqRange = dconf['net']['cochThalFreqRange'] # [1000, 2000]

# these params added from Christoph Metzner branch
# these control strength of thalamic inputs to different subpopulations
cfg.thalL4PV = dconf['net']['thalL4PV'] # 0.21367245896786016 # 0.3201033836037148 # 0.261333644625591   # 0.21367245896786016 # 0.25 
cfg.thalL4SOM = dconf['net']['thalL4SOM'] # 0.24260966747847523 # 0.3200462291706402 # 0.2612645277258505 # 0.24260966747847523 # 0.25 
cfg.thalL4E = dconf['net']['thalL4E'] # 1.9540886147587417 # 2.8510831744854714 # 2.3199103007567827   # 1.9540886147587417 # 2.0
cfg.thalL4VIP = dconf['net']['thalL4VIP'] # 1.0
cfg.thalL4NGF = dconf['net']['thalL4NGF'] # 1.0
cfg.thalL1NGF = dconf['net']['thalL1NGF'] # 1.0
cfg.ENGF1 = dconf['net']['ENGF1'] # 1.0 # modulates strength of synaptic connections from E -> NGF1 neurons

# modulates strength of connections from L4 -> L3 by different target subpopulations
#  these next 5 param values are from after generation 59 of optunaERP_24mar5_ (optimized L3 sink) 
cfg.L4L3E    = dconf['net']['L4L3E'] # 1.0188377611592279 # 1.0
cfg.L4L3PV   = dconf['net']['L4L3PV'] # 0.9829655631376849 # 1.0
cfg.L4L3SOM  = dconf['net']['L4L3SOM'] # 0.9647203483395813 # 1.0
cfg.L4L3VIP = dconf['net']['L4L3VIP'] # 1.039136847713827 # 1.0
cfg.L4L3NGF = dconf['net']['L4L3NGF'] # 0.9119964748686543 # 1.0

cfg.addSubConn = 1 # specifies to put synapses on particular subcellular target locations

## full weight conn matrix
with open('conn/conn.pkl', 'rb') as fileObj: connData = pickle.load(fileObj)
cfg.wmat = connData['wmat']

#------------------------------------------------------------------------------
# Background inputs
#------------------------------------------------------------------------------
cfg.addBkgConn = 1
cfg.noiseBkg = 1.0  # firing rate random noise
cfg.delayBkg = 5.0  # (ms)
cfg.startBkg = 0  # start at 0 ms

# cfg.weightBkg = {'IT': 12.0, 'ITS4': 0.7, 'PT': 14.0, 'CT': 14.0,
#                 'PV': 28.0, 'SOM': 5.0, 'NGF': 80.0, 'VIP': 9.0,
#                 'TC': 1.8, 'HTC': 1.55, 'RE': 9.0, 'TI': 3.6}
cfg.rateBkg = {'exc': 40, 'inh': 40}

## options to provide external sensory input
#cfg.randomThalInput = True  # provide random bkg inputs spikes (NetStim) to thalamic populations 

# parameters to generate realistic  auditory thalamic inputs using Brian Hears
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
else:
  cfg.cochlearThalInput = False  

#------------------------------------------------------------------------------
# Current inputs 
#------------------------------------------------------------------------------
cfg.addIClamp = dconf['addIClamp'] # and 'IClamp' in dconf # whether to apply current clamp
# print('cfg.addIClamp = ', cfg.addIClamp, dconf['IClamp'])
cfg.addRIClamp = dconf['addRIClamp'] # and 'RIClamp in dconf

#------------------------------------------------------------------------------
# NetStim inputs 
#------------------------------------------------------------------------------

cfg.addNetStim = dconf['addNetStim'] # whether to add additional external stimuli (not background stimuli)

if dconf['addNetStim']:
  for pop,dns in dconf['NetStim'].items():
    cfg.__dict__['NetStim'+pop+'_r'] = {'pop': pop,  'ynorm': [0,1], 'sec': dns['sec'], 'loc': dns['loc'],\
                                        'synMech': dns['synMech'], 'synMechWeightFactor': [1.0], 'start': dns['start'],\
                                        'interval': dns['interval'], 'noise': dns['noise'], 'number': dns['number'],\
 	                                'weight': dns['weight'],'delay':dns['delay']}
cfg.tune = {}


# ------------------------ ADD PARAM VALUES FROM .JSON FILES: 
# COMMENT THIS OUT IF USING GCP !!! ONLY USE IF USING NEUROSIM!!! 
import json

with open('data/v34_batch25/trial_2142/trial_2142_cfg.json', 'rb') as f:       # 'data/salva_runs/v29_batch3_trial_13425_cfg.json'
	cfgLoad = json.load(f)['simConfig']


## UPDATE CORTICAL GAIN PARAMS 
cfg.EEGain = cfgLoad['EEGain']
cfg.EIGain = cfgLoad['EIGain']
cfg.IEGain = cfgLoad['IEGain']
cfg.IIGain = cfgLoad['IIGain']

cfg.EICellTypeGain['PV'] =  cfgLoad['EICellTypeGain']['PV']
cfg.EICellTypeGain['SOM'] = cfgLoad['EICellTypeGain']['SOM']
cfg.EICellTypeGain['VIP'] = cfgLoad['EICellTypeGain']['VIP']
cfg.EICellTypeGain['NGF'] = cfgLoad['EICellTypeGain']['NGF']

cfg.IECellTypeGain['PV'] = cfgLoad['IECellTypeGain']['PV']
cfg.IECellTypeGain['SOM'] = cfgLoad['IECellTypeGain']['SOM']
cfg.IECellTypeGain['VIP'] = cfgLoad['IECellTypeGain']['VIP']
cfg.IECellTypeGain['NGF'] = cfgLoad['IECellTypeGain']['NGF']

cfg.EILayerGain['1'] = cfgLoad['EILayerGain']['1']
cfg.IILayerGain['1'] = cfgLoad['IILayerGain']['1']

cfg.EELayerGain['2'] = cfgLoad['EELayerGain']['2']
cfg.EILayerGain['2'] = cfgLoad['EILayerGain']['2']
cfg.IELayerGain['2'] = cfgLoad['IELayerGain']['2']
cfg.IILayerGain['2'] = cfgLoad['IILayerGain']['2']


cfg.EELayerGain['3'] = cfgLoad['EELayerGain']['3']
cfg.EILayerGain['3'] = cfgLoad['EILayerGain']['3']
cfg.IELayerGain['3'] = cfgLoad['IELayerGain']['3']
cfg.IILayerGain['3'] = cfgLoad['IILayerGain']['3']


cfg.EELayerGain['4'] = cfgLoad['EELayerGain']['4']
cfg.EILayerGain['4'] = cfgLoad['EILayerGain']['4']
cfg.IELayerGain['4'] = cfgLoad['IELayerGain']['4']
cfg.IILayerGain['4'] = cfgLoad['IILayerGain']['4']

cfg.EELayerGain['5A'] = cfgLoad['EELayerGain']['5A']
cfg.EILayerGain['5A'] = cfgLoad['EILayerGain']['5A']
cfg.IELayerGain['5A'] = cfgLoad['IELayerGain']['5A']
cfg.IILayerGain['5A'] = cfgLoad['IILayerGain']['5A']

cfg.EELayerGain['5B'] = cfgLoad['EELayerGain']['5B']
cfg.EILayerGain['5B'] = cfgLoad['EILayerGain']['5B']
cfg.IELayerGain['5B'] = cfgLoad['IELayerGain']['5B'] 
cfg.IILayerGain['5B'] = cfgLoad['IILayerGain']['5B']

cfg.EELayerGain['6'] = cfgLoad['EELayerGain']['6']  
cfg.EILayerGain['6'] = cfgLoad['EILayerGain']['6']  
cfg.IELayerGain['6'] = cfgLoad['IELayerGain']['6']  
cfg.IILayerGain['6'] = cfgLoad['IILayerGain']['6']

# UPDATE THALAMIC GAIN PARAMS
cfg.thalamoCorticalGain = cfgLoad['thalamoCorticalGain']
cfg.intraThalamicGain = cfgLoad['intraThalamicGain']
cfg.EbkgThalamicGain = cfgLoad['EbkgThalamicGain']
cfg.IbkgThalamicGain = cfgLoad['IbkgThalamicGain']

cfg.thalamoCorticalGain = dconf['net']['thalamoCorticalGain'] # use value from sim.json; original = 2.1111391118965863

# print('cfg.EELayerGain',cfg.EELayerGain,'cfg.EILayerGain',cfg.EILayerGain,'cfg.IELayerGain:',cfg.IELayerGain,'cfg.IILayerGain',cfg.IILayerGain)

cfg.EELayerGain = dconf['net']['EELayerGain']
cfg.EILayerGain = dconf['net']['EILayerGain']
cfg.IELayerGain = dconf['net']['IELayerGain']
cfg.IILayerGain = dconf['net']['IILayerGain']

# UPDATE WMAT VALUES
cfg.wmat = cfgLoad['wmat']

if dconf['sim']['useICThal']:
  cfg.ICThalInput = {'file': dconf['ICThalInput']['file'], # BBN_trials/ICoutput_CF_9600_10400_wav_BBN_100ms_burst_AN.mat',
                     'startTime': list(np.arange(dconf['ICThalInput']['onset'], dconf['ICThalInput']['offset'], dconf['ICThalInput']['interval'])), 
                     'weightECore': cfg.ICThalweightECore,
                     'weightICore': cfg.ICThalweightICore,
                     'probECore': cfg.ICThalprobECore, 
                     'probICore': cfg.ICThalprobICore,
                     'probEMatrix': cfg.ICThalprobEMatrix,
                     'probIMatrix': cfg.ICThalprobIMatrix,
                     'MatrixCoreFactor': cfg.ICThalMatrixCoreFactor,
                     'seed': 1}  # SHOULD THIS BE ZERO?
else:
  cfg.ICThalInput = False


cfg.scale = dconf['net']['scale'] 
cfg.sizeY = dconf['net']['sizeY'] 
cfg.sizeX = dconf['net']['sizeX'] 
cfg.sizeZ = dconf['net']['sizeZ']
cfg.scaleDensity = dconf['net']['scaleDensity'] #0.25 #1.0 #0.075 # Should be 1.0 unless need lower cell density for test simulation or visualization
  
cfg.EEGain = dconf['net']['EEGain'] 
cfg.EIGain = dconf['net']['EIGain']
cfg.IEGain = dconf['net']['IEGain']
cfg.IIGain = dconf['net']['IIGain']

cfg.EbkgThalamicGain = dconf['EbkgThalamicGain']
cfg.IbkgThalamicGain = dconf['IbkgThalamicGain']