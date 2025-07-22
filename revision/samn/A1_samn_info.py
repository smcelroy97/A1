import json
import pickle


dconf = {
    "verbose": 0,
    "sim": {
        "duration": 200,
        "dt": 0.05,
        "verbose": 0,
        "recordStep": 0.1,
        "name": "25jul15_ISIRefracBase_",
        "doquit": 1,
        "doplot": 0,
        "dosave": 1, 
        "saveCellSecs": 1,
        "saveCellConns": 0,
        "useICThal": 0,
        "useCochleaThal": 0,
        "recordDipole": 0,
        "ncelltracerecord": 5,
        "recordFullTraces": 1
    },
    "net": {
        "connseed": 1,
        "stimseed": 1,
        "scale": 1.0,
        "sizeY": 2000.0,
        "sizeX": 200.0,
        "sizeZ": 200.0,
        "scaleDensity": 1.0,
        "EEGain": 1.1,
        "EIGain": 1.6313576020869256,
        "IEGain": 2.06,
        "IIGain": 1.4102431748127964,
        "EELayerGain": {"1": 1.0, "2": 1.1392556114489, "3": 0.2627680775261009, "4": 0.7953549349740079, "5A": 1.107062263790829, "5B": 0.1873673565713772, "6": 0.6},
        "EILayerGain": {"1": 0.827750821266419, "2": 0.8309591864633213, "3": 0.2606080713427127, "4": 0.7, "5A": 0.9777414771947963, "5B": 1.2194384057226428, "6": 2.661195004653538},
        "IELayerGain": {"1": 1.0, "2": 0.8766937284048854, "3": 0.5609281169449685, "4": 1.870729555191084, "5A": 3.566320604507868, "5B": 0.7695785463331726, "6": 4.9},
        "IILayerGain": {"1": 1.1305254604890966, "2": 1.1428945741399408, "3": 0.2896903197397815, "4": 1.08, "5A": 0.5982384402236298, "5B": 0.879452953038821, "6": 0.4784462642417754},  
        "ICThalweightECore": 0.8350476447841453,
        "ICThalweightICore": 0.2114492149101151,
        "ICThalprobECore": 0.163484173596043,
        "ICThalprobICore": 0.0936669688856933,
        "ICThalMatrixCoreFactor": 0.1,
        "cochThalweightECore": 0.225,
        "cochThalweightICore": 0.0675,
        "cochThalweightEMatrix": 0.1125,
        "cochThalweightIMatrix": 0.0675,
        "cochThalprobECore": 0.9,
        "cochThalprobICore": 0.45,
        "cochThalprobEMatrix": 0.1125,
        "cochThalprobIMatrix": 0.0028,
        "cochThalFreqRange": [750, 1250],
        "fracHSRMSRLSR": [0.0, 0.0, 1.0],
        "thalL4PV": 0.21367245896786016,
        "thalL4SOM": 0.24260966747847523,
        "thalL4E": 2,
        "thalL4VIP": 1.0,
        "thalL4NGF": 1.0,
        "thalL1NGF": 1.0,
        "ENGF1": 1.0,
        "L4L3E": 1.0,
        "L4L3PV": 1.0,
        "L4L3SOM": 1.0,
        "L4L3VIP": 1.0,
        "L4L3NGF": 1.0,
        "EEPopGain": {"IT2": 1.3125, "IT3": 1.55, "ITP4": 1.0, "ITS4": 1.0, "IT5A": 1.05, "CT5A": 1.1500000000000001, "IT5B": 0.425, "CT5B": 1.1500000000000001, "PT5B": 1.05, "IT6": 1.05, "CT6": 1.05},
        "EIPopGain": {"NGF1": 1.0, "SOM2": 1.0, "PV2": 1.0, "VIP2": 1.0, "NGF2": 1.0, "SOM3": 1.0, "PV3": 1.0, "VIP3": 1.0, "NGF3": 1.0, "SOM4": 1.0, "PV4": 1.0, "VIP4": 1.0, "NGF4": 1.0, "SOM5A": 1.0, "PV5A": 1.4, "VIP5A": 1.25, "NGF5A": 0.8, "SOM5B": 1.0, "PV5B": 1.45, "VIP5B": 1.4, "NGF5B": 0.9500000000000001, "SOM6": 1.0, "PV6": 1.4, "VIP6": 1.3499999999999999, "NGF6": 0.65},
        "ThalamicCoreLambda": 50.0,
        "addIntraThalamicConn": 1,
        "addCorticoThalamicConn": 1,
        "addThalamoCorticalConn": 1,
        "thalamoCorticalGain" : 3.0,
        "corticoThalamicGain": 1.0,
        "intraThalamicEEGain": 1.0,
        "intraThalamicEIGain": 1.0,
        "intraThalamicIEGain": 1.0,
        "intraThalamicIIGain": 1.0,
        "intraThalamicCoreEEGain": 1.0,
        "intraThalamicCoreEIGain": 1.5,
        "intraThalamicCoreIEGain": 1.5,
        "intraThalamicCoreIIGain": 1.0      
    },
    "ICThalInput": {"onset": 5000, "offset":12000, "interval": 1000, "file": "data/ICoutput/ICoutput_CF_5256_6056_wav_BBN_100ms_burst.mat"},
    "CochlearThalInput" : {
        "lonset":[0],      
        "numCenterFreqs": 1,
        "freqRange": [125, 20000],
        "loudnessScale": 1,
        "lfnwave":["wav/silence6.8s.wav"],
        "autoSilence": 0,
        "useLinearCF": 0,
        "saveDcoch": 1,
        "readDcoch": "data/25jan24_G_dcoch.pkl"
    },
    "EbkgThalamicGain": 0.392,
    "IbkgThalamicGain": 1.96,
    "syn": {
        "GABABThal": {"mod": "MyExp2SynBB", "tau1": 41, "tau2": 642, "e": -105},
        "GABABCtx": {"mod": "MyExp2SynBB", "tau1": 41, "tau2": 642, "e": -105},      
        "synWeightFractionThal": {"Thal":{"I": {"E": [0.9, 0.4], "I":[1.0,0.0]}},"Ctx":{"I": {"E": [1.0,0.0], "I":[1.0]}}},
        "synWeightFractionNGF":  {"E":[0.5, 1.0],"I":[1.0]},
        "synWeightFractionSOM":  {"E":[0.9, 0.2],"I":[1.0]},
        "synWeightFractionIE": [0.9, 0.1],
        "synWeightFractionII": [1.0],
        "synWeightFractionEE": [0.5, 0.5],
        "synWeightFractionEI": [0.5, 0.5],
        "synWeightFractionEI_CustomCort": [0.5, 0.5],
        "synWeightFractionENGF": [0.834, 0.166]
    },
    "addIClamp": 0,
    "IClamp" : {
        "ITP4": {"delay": 500, "dur": 7500, "amp": 0.5, "sec": "soma", "loc": 0.5},
        "ITS4": {"delay": 500, "dur": 7500, "amp": 0.5, "sec": "soma", "loc": 0.5}
    },
    "addRIClamp": 0,
    "RIClamp" : {
        "TCM": {"delay": 100, "dur": 100, "amp": 0.375, "sec": "soma", "loc": 0.5, "number": 25, "interval": 250}
    },
    "addNetStim": 0,
    "NetStim": {
        "TC": {"start": 3000, "interval": 150.0, "weight":10.0, "sec": "soma", "loc": 0.5, "synMech": "AMPA","delay":0,"number":15,"noise":0},
        "HTC": {"start": 3000, "interval": 150.0, "weight":10.0, "sec": "soma", "loc": 0.5, "synMech": "AMPA","delay":0,"number":15,"noise":0},
        "TCM": {"start": 3000, "interval": 150.0, "weight":5.0, "sec": "soma", "loc": 0.5, "synMech": "AMPA","delay":0,"number":15,"noise":0}       
    }
}

cfg = {}

def cells():
    cfg.weightNormThreshold = 5.0  # maximum weight normalization factor with respect to the somaw
    cfg.weightNormScaling = {'NGF_reduced': 1.0, 'ITS4_reduced': 1.0}
    cfg.ihGbar = 1.0 
    cfg.KgbarFactor = 1.0
  
def synapses():
    cfg.AMPATau2Factor = 1.0
    cfg.synWeightFractionEE = dconf['syn']['synWeightFractionEE'] # [0.5, 0.5] # E->E AMPA to NMDA ratio
    cfg.synWeightFractionEI = dconf['syn']['synWeightFractionEI'] # [0.5, 0.5] # E->I AMPA to NMDA ratio
    cfg.synWeightFractionEI_CustomCort = dconf['syn']['synWeightFractionEI_CustomCort'] # [0.5, 0.5] # E->I AMPA to NMDA ratio custom for cortex NMDA manipulation
    cfg.synWeightFractionNGF = dconf['syn']['synWeightFractionNGF'] # {'E':[0.5, 0.5],'I':[0.9,0.1]} # NGF GABAA to GABAB ratio when connecting to E , I neurons
    cfg.synWeightFractionSOM = dconf['syn']['synWeightFractionSOM'] # {'E':[0.9, 0.1],'I':[0.9,0.1]} # SOM GABAA to GABAB ratio when connection to E , I neurons
    cfg.synWeightFractionENGF = dconf['syn']['synWeightFractionENGF'] # [0.834, 0.166] # AMPA to NMDA ratio for E -> NGF connections
    cfg.useHScale = False

def network():
    cfg.singleCellPops = False #True #False
    cfg.singlePop = ''
    cfg.removeWeightNorm = False

def connectivity_dconf():
    cfg.synWeightFractionIE = dconf['syn']['synWeightFractionIE'] # [1.0] # this is set to 1 for PV,VIP; for SOM,NGF have other param for GABAASlow to GABAB ratio
    cfg.synWeightFractionII = dconf['syn']['synWeightFractionII'] # [1.0]  # I->I uses single synapse mechanism

    ## E/I->E/I layer weights (L1-3, L4, L5, L6)
    cfg.EELayerGain = {'1': 1.0, '2': 1.0, '3': 1.0, '4': 1.0 , '5A': 1.0, '5B': 1.0, '6': 1.0}
    cfg.EILayerGain = {'1': 1.0, '2': 1.0, '3': 1.0, '4': 1.0 , '5A': 1.0, '5B': 1.0, '6': 1.0}
    cfg.IELayerGain = {'1': 1.0, '2': 1.0, '3': 1.0, '4': 1.0 , '5A': 1.0, '5B': 1.0, '6': 1.0}
    cfg.IILayerGain = {'1': 1.0, '2': 1.0, '3': 1.0, '4': 1.0 , '5A': 1.0, '5B': 1.0, '6': 1.0}

    # E -> E based on postsynaptic cortical E neuron population
    cfg.EEPopGain = dconf['net']['EEPopGain']
    # gains from E -> I based on postsynaptic cortical I neuron population
    cfg.EIPopGain = dconf['net']['EIPopGain']

    ## E->I by target cell type
    cfg.EICellTypeGain = {'PV': 1.0, 'SOM': 1.0, 'VIP': 1.0, 'NGF': 1.0}
    ## I->E by target cell type
    cfg.IECellTypeGain = {'PV': 1.0, 'SOM': 1.0, 'VIP': 1.0, 'NGF': 1.0}

    # Thalamic
    cfg.corticoThalamicGain = dconf['net']['corticoThalamicGain']

    def ic_thal():
        # these params control IC -> Thalamic Core
        cfg.ICThalweightECore = dconf['net']['ICThalweightECore'] # 0.8350476447841453 # 1.0218574230414905 # 1.1366391725804097  # 0.8350476447841453 # 1.0
        cfg.ICThalweightICore = dconf['net']['ICThalweightICore'] # 0.2114492149101151 # 0.20065170901643178 # 0.21503725192597786 # 0.2114492149101151 # 0.25
        cfg.ICThalprobECore = dconf['net']['ICThalprobECore'] # 0.163484173596043 # 0.17524000437877066 # 0.21638972066571394   # 0.163484173596043 # 0.19
        cfg.ICThalprobICore = dconf['net']['ICThalprobICore'] # 0.0936669688856933 # 0.0978864963550709 # 0.11831534696879886   # 0.0936669688856933 # 0.12
        # these params control IC -> Thalamic Matrix
        cfg.ICThalMatrixCoreFactor = dconf['net']['ICThalMatrixCoreFactor'] # 0.1 # 0.0988423213016316 # 0.11412487872986073 # 0.1 # this is used to scale weights to thalamic matrix neurons in netParams.py
        cfg.ICThalprobEMatrix = cfg.ICThalprobECore 
        cfg.ICThalprobIMatrix = cfg.ICThalprobICore

    def coch_thal():
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

## full weight conn matrix
with open('conn/conn.pkl', 'rb') as fileObj:
    connData = pickle.load(fileObj)
cfg.wmat = connData['wmat']

def bkg():
    cfg.addBkgConn = 1
    cfg.noiseBkg = 1.0  # firing rate random noise
    cfg.delayBkg = 5.0  # (ms)
    cfg.startBkg = 0  # start at 0 ms
    cfg.rateBkg = {'exc': 40, 'inh': 40}

def coch_thal():
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

def inputs():
    cfg.addIClamp = dconf['addIClamp'] # and 'IClamp' in dconf # whether to apply current clamp
    cfg.addRIClamp = dconf['addRIClamp'] # and 'RIClamp in dconf

    cfg.addNetStim = dconf['addNetStim'] # whether to add additional external stimuli (not background stimuli)

    if dconf['addNetStim']:
        for pop,dns in dconf['NetStim'].items():
            cfg.__dict__['NetStim'+pop+'_r'] = {
                'pop': pop,  'ynorm': [0,1], 'sec': dns['sec'], 'loc': dns['loc'],
                'synMech': dns['synMech'], 'synMechWeightFactor': [1.0], 'start': dns['start'],
                'interval': dns['interval'], 'noise': dns['noise'], 'number': dns['number'],
                'weight': dns['weight'],'delay':dns['delay']
            }

# 'data/v34_batch25/trial_2142/trial_2142_cfg.json'
cfgLoad = {}

def connectivity_cfg_load():

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

def gains_again():
    cfg.EELayerGain = dconf['net']['EELayerGain']
    cfg.EILayerGain = dconf['net']['EILayerGain']
    cfg.IELayerGain = dconf['net']['IELayerGain']
    cfg.IILayerGain = dconf['net']['IILayerGain']

    cfg.EEGain = dconf['net']['EEGain'] 
    cfg.EIGain = dconf['net']['EIGain']
    cfg.IEGain = dconf['net']['IEGain']
    cfg.IIGain = dconf['net']['IIGain']

    cfg.EbkgThalamicGain = dconf['EbkgThalamicGain']
    cfg.IbkgThalamicGain = dconf['IbkgThalamicGain']

# UPDATE WMAT VALUES
cfg.wmat = cfgLoad['wmat']

def ic_thal_2():
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

def scale():

    cfg.scale = dconf['net']['scale'] 
    cfg.sizeY = dconf['net']['sizeY'] 
    cfg.sizeX = dconf['net']['sizeX'] 
    cfg.sizeZ = dconf['net']['sizeZ']
    cfg.scaleDensity = dconf['net']['scaleDensity']


x =1
    