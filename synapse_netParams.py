from netpyne.batchtools import specs
import pickle
import json
from synapse_cfg import cfg
netParams = specs.NetParams()   # object of class NetParams to store the network parameters

pops = cfg.allpops
TEpops = ['TC', 'TCM', 'HTC']
TIpops = ['IRE', 'IREM', 'TI', 'TIM']
prePop = cfg.prePop
stimName = prePop + '_stim'

netParams.scale = cfg.scale  # Scale factor for number of cells # NOT DEFINED YET! 3/11/19 # How is this different than scaleDensity?
netParams.sizeX = cfg.sizeX  # x-dimension (horizontal length) size in um
netParams.sizeY = cfg.sizeY  # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = cfg.sizeZ  # z-dimension (horizontal depth) size in um
netParams.shape = 'cylinder'  # cylindrical (column-like) volume

# ------------------------------------------------------------------------------
# General connectivity parameters
# ------------------------------------------------------------------------------
netParams.scaleConnWeight = 1.0  # Connection weight scale factor (default if no model specified)
netParams.scaleConnWeightModels = {'HH_reduced': 1.0, 'HH_full': 1.0}  # scale conn weight factor for each cell model
netParams.scaleConnWeightNetStims = 1.0  # 0.5  # scale conn weight factor for NetStims
netParams.defaultThreshold = 0.0  # spike threshold, 10 mV is NetCon default, lower it for all cells
netParams.defaultDelay = 2.0  # default conn delay (ms)
netParams.propVelocity = 500.0  # propagation velocity (um/ms)
netParams.probLambda = 100.0  # length constant (lambda) for connection probability decay (um)
ThalamicCoreLambda = 50.0
# ------------------------------------------------------------------------------
# Cell parameters
# ------------------------------------------------------------------------------
## List of E and I pops to use later on
Epops = ['IT2', 'IT3', 'ITP4', 'ITS4',
         'IT5A', 'CT5A', 'IT5B', 'CT5B',
         'PT5B', 'IT6', 'CT6']  # all layers

Ipops = ['NGF1',                            # L1
         'PV2', 'SOM2', 'VIP2', 'NGF2',      # L2
         'PV3', 'SOM3', 'VIP3', 'NGF3',      # L3
         'PV4', 'SOM4', 'VIP4', 'NGF4',      # L4
         'PV5A', 'SOM5A', 'VIP5A', 'NGF5A',  # L5A
         'PV5B', 'SOM5B', 'VIP5B', 'NGF5B',  # L5B
         'PV6', 'SOM6', 'VIP6', 'NGF6']      # L6

Etypes = ['IT', 'ITS4', 'PT', 'CT']
Itypes = ['PV', 'SOM', 'VIP', 'NGF']

cellModels = ['HH_reduced', 'HH_full']  # List of cell models

# II: 100-950, IV: 950-1250, V: 1250-1550, VI: 1550-2000
layer = {'1': [0.00, 0.05], '2': [0.05, 0.08], '3': [0.08, 0.475], '4': [0.475, 0.625],
         '5A': [0.625, 0.667], '5B': [0.667, 0.775], '6': [0.775, 1], 'thal': [1.2, 1.4],
         'cochlear': [1.6, 1.601]}  # normalized layer boundaries

layerGroups = {
    '1-3': [layer['1'][0], layer['3'][1]],    # L1-3
    '4': layer['4'],                                   # L4
    '5': [layer['5A'][0], layer['5B'][1]],  # L5A-5B
    '6': layer['6']}                                  # L6

# ------------------------------------------------------------------------------
## Load cell rules previously saved using netpyne format (DOES NOT INCLUDE VIP, NGF and spiny stellate)
## include conditions ('conds') for each cellRule
cellParamLabels = ['IT2_reduced', 'IT3_reduced', 'ITP4_reduced', 'ITS4_reduced',
                   'IT5A_reduced', 'CT5A_reduced', 'IT5B_reduced',
                   'PT5B_reduced', 'CT5B_reduced', 'IT6_reduced', 'CT6_reduced',
                   'PV_reduced', 'SOM_reduced', 'VIP_reduced', 'NGF_reduced',
                   'RE_reduced', 'TC_reduced', 'HTC_reduced', 'TI_reduced']  # , 'TI_reduced']

for ruleLabel in cellParamLabels:
    netParams.loadCellParamsRule(label=ruleLabel, fileName='cells/' + ruleLabel + '_cellParams.json')  # Load cellParams for each of the above cell subtype

# ------------------------------------------------------------------------------
# Population parameters
# ------------------------------------------------------------------------------

## load densities
with open('cells/cellDensity.pkl', 'rb') as fileObj:
    density = pickle.load(fileObj)['density']
density = {k: [x * cfg.scaleDensity for x in v] for k, v in density.items()}  # Scale densities

### Stim Pop
# create custom list of spike times
spkTimes = [0]

netParams.popParams[stimName] = {'cellModel': 'VecStim', 'numCells': 1, 'spkTimes': spkTimes}  # VecStim with spike times

### LAYER 1:
netParams.popParams['NGF1'] = {'cellType': 'NGF', 'cellModel': 'HH_reduced', 'ynormRange': layer['1'],   'density': density[('A1', 'nonVIP')][0]}

## LAYER 2:
netParams.popParams['IT2'] =     {'cellType': 'IT',  'cellModel': 'HH_reduced',  'ynormRange': layer['2'],   'density': density[('A1','E')][1]}     # cfg.cellmod for 'cellModel' in M1 netParams.py
netParams.popParams['SOM2'] =    {'cellType': 'SOM', 'cellModel': 'HH_reduced',   'ynormRange': layer['2'],   'density': density[('A1','SOM')][1]}
netParams.popParams['PV2'] =     {'cellType': 'PV',  'cellModel': 'HH_reduced',   'ynormRange': layer['2'],   'density': density[('A1','PV')][1]}
netParams.popParams['VIP2'] =    {'cellType': 'VIP', 'cellModel': 'HH_reduced',   'ynormRange': layer['2'],   'density': density[('A1','VIP')][1]}
netParams.popParams['NGF2'] =    {'cellType': 'NGF', 'cellModel': 'HH_reduced',   'ynormRange': layer['2'],   'density': density[('A1','nonVIP')][1]}

## LAYER 3:
netParams.popParams['IT3'] =     {'cellType': 'IT',  'cellModel': 'HH_reduced',  'ynormRange': layer['3'],   'density': density[('A1','E')][1]}  # CHANGE DENSITY
netParams.popParams['SOM3'] =    {'cellType': 'SOM', 'cellModel': 'HH_reduced',   'ynormRange': layer['3'],   'density': density[('A1','SOM')][1]}  # CHANGE DENSITY
netParams.popParams['PV3'] =     {'cellType': 'PV',  'cellModel': 'HH_reduced',   'ynormRange': layer['3'],   'density': density[('A1','PV')][1]}  # CHANGE DENSITY
netParams.popParams['VIP3'] =    {'cellType': 'VIP', 'cellModel': 'HH_reduced',   'ynormRange': layer['3'],   'density': density[('A1','VIP')][1]}  # CHANGE DENSITY
netParams.popParams['NGF3'] =    {'cellType': 'NGF', 'cellModel': 'HH_reduced',   'ynormRange': layer['3'],   'density': density[('A1','nonVIP')][1]}


## LAYER 4:
netParams.popParams['ITP4'] =	 {'cellType': 'IT', 'cellModel': 'HH_reduced',  'ynormRange': layer['4'],   'density': 0.5*density[('A1','E')][2]}      # CHANGE DENSITY
netParams.popParams['ITS4'] =	 {'cellType': 'ITS4', 'cellModel': 'HH_reduced', 'ynormRange': layer['4'],  'density': 0.5*density[('A1','E')][2]}      # CHANGE DENSITY
netParams.popParams['SOM4'] = 	 {'cellType': 'SOM', 'cellModel': 'HH_reduced',   'ynormRange': layer['4'],  'density': density[('A1','SOM')][2]}
netParams.popParams['PV4'] = 	 {'cellType': 'PV', 'cellModel': 'HH_reduced',   'ynormRange': layer['4'],   'density': density[('A1','PV')][2]}
netParams.popParams['VIP4'] =	 {'cellType': 'VIP', 'cellModel': 'HH_reduced',   'ynormRange': layer['4'],  'density': density[('A1','VIP')][2]}
netParams.popParams['NGF4'] =    {'cellType': 'NGF', 'cellModel': 'HH_reduced',   'ynormRange': layer['4'],  'density': density[('A1','nonVIP')][2]}

# ### LAYER 5A:
netParams.popParams['IT5A'] =     {'cellType': 'IT',  'cellModel': 'HH_reduced',   'ynormRange': layer['5A'], 	'density': 0.5*density[('A1','E')][3]}
netParams.popParams['CT5A'] =     {'cellType': 'CT',  'cellModel': 'HH_reduced',   'ynormRange': layer['5A'],   'density': 0.5*density[('A1','E')][3]}
netParams.popParams['SOM5A'] =    {'cellType': 'SOM', 'cellModel': 'HH_reduced',    'ynormRange': layer['5A'],	'density': density[('A1','SOM')][3]}
netParams.popParams['PV5A'] =     {'cellType': 'PV',  'cellModel': 'HH_reduced',    'ynormRange': layer['5A'],	'density': density[('A1','PV')][3]}
netParams.popParams['VIP5A'] =    {'cellType': 'VIP', 'cellModel': 'HH_reduced',    'ynormRange': layer['5A'],   'density': density[('A1','VIP')][3]}
netParams.popParams['NGF5A'] =    {'cellType': 'NGF', 'cellModel': 'HH_reduced',    'ynormRange': layer['5A'],   'density': density[('A1','nonVIP')][3]}

### LAYER 5B:
netParams.popParams['IT5B'] =     {'cellType': 'IT',  'cellModel': 'HH_reduced',   'ynormRange': layer['5B'], 	'density': (1/3)*density[('A1','E')][4]}
netParams.popParams['CT5B'] =     {'cellType': 'CT',  'cellModel': 'HH_reduced',   'ynormRange': layer['5B'],   'density': (1/3)*density[('A1','E')][4]}
netParams.popParams['PT5B'] =     {'cellType': 'PT',  'cellModel': 'HH_reduced',   'ynormRange': layer['5B'], 	'density': (1/3)*density[('A1','E')][4]}
netParams.popParams['SOM5B'] =    {'cellType': 'SOM', 'cellModel': 'HH_reduced',    'ynormRange': layer['5B'],   'density': density[('A1', 'SOM')][4]}
netParams.popParams['PV5B'] =     {'cellType': 'PV',  'cellModel': 'HH_reduced',    'ynormRange': layer['5B'],	'density': density[('A1','PV')][4]}
netParams.popParams['VIP5B'] =    {'cellType': 'VIP', 'cellModel': 'HH_reduced',    'ynormRange': layer['5B'],   'density': density[('A1','VIP')][4]}
netParams.popParams['NGF5B'] =    {'cellType': 'NGF', 'cellModel': 'HH_reduced',    'ynormRange': layer['5B'],   'density': density[('A1','nonVIP')][4]}

# # ### LAYER 6:
netParams.popParams['IT6'] =     {'cellType': 'IT',  'cellModel': 'HH_reduced',  'ynormRange': layer['6'],   'density': 0.5*density[('A1','E')][5]}
netParams.popParams['CT6'] =     {'cellType': 'CT',  'cellModel': 'HH_reduced',  'ynormRange': layer['6'],   'density': 0.5*density[('A1','E')][5]}
netParams.popParams['SOM6'] =    {'cellType': 'SOM', 'cellModel': 'HH_reduced',   'ynormRange': layer['6'],   'density': density[('A1','SOM')][5]}
netParams.popParams['PV6'] =     {'cellType': 'PV',  'cellModel': 'HH_reduced',   'ynormRange': layer['6'],   'density': density[('A1','PV')][5]}
netParams.popParams['VIP6'] =    {'cellType': 'VIP', 'cellModel': 'HH_reduced',   'ynormRange': layer['6'],   'density': density[('A1','VIP')][5]}
netParams.popParams['NGF6'] =    {'cellType': 'NGF', 'cellModel': 'HH_reduced',   'ynormRange': layer['6'],   'density': density[('A1','nonVIP')][5]}


# ### THALAMIC POPULATIONS (from prev model)
# thalDensity = density[('A1','PV')][2] * 1.25  # temporary estimate (from prev model)
#
# netParams.popParams['TC'] =     {'cellType': 'TC',  'cellModel': 'HH_reduced',  'ynormRange': layer['thal'],   'density': 0.75*thalDensity}
# netParams.popParams['TCM'] =    {'cellType': 'TC',  'cellModel': 'HH_reduced',  'ynormRange': layer['thal'],   'density': thalDensity}
# netParams.popParams['HTC'] =    {'cellType': 'HTC', 'cellModel': 'HH_reduced',  'ynormRange': layer['thal'],   'density': 0.25*thalDensity}
# netParams.popParams['IRE'] =    {'cellType': 'RE',  'cellModel': 'HH_reduced',  'ynormRange': layer['thal'],   'density': thalDensity}
# netParams.popParams['IREM'] =   {'cellType': 'RE', 'cellModel': 'HH_reduced',   'ynormRange': layer['thal'],   'density': thalDensity}
# netParams.popParams['TI'] =     {'cellType': 'TI',  'cellModel': 'HH_reduced',  'ynormRange': layer['thal'],   'density': 0.33 * thalDensity} ## Winer & Larue 1996; Huang et al 1999
# netParams.popParams['TIM'] =    {'cellType': 'TI',  'cellModel': 'HH_reduced',  'ynormRange': layer['thal'],   'density': 0.33 * thalDensity} ## Winer & Larue 1996; Huang et al 1999

for pop in netParams.popParams.values(): pop['numCells'] = 1

netParams.synMechParams['NMDA'] = {'mod': 'MyExp2SynNMDABB', 'tau1NMDA': 15, 'tau2NMDA': 150, 'e': 0}
netParams.synMechParams['AMPA'] = {'mod':'MyExp2SynBB', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}
netParams.synMechParams['GABAB'] = {"mod": "MyExp2SynBB", "tau1": 41, "tau2": 642, "e": -105}
netParams.synMechParams['GABAA'] = {'mod':'MyExp2SynBB', 'tau1': 0.07, 'tau2': 18.2, 'e': -80}
netParams.synMechParams['GABAA_VIP'] = {'mod':'MyExp2SynBB', 'tau1': 0.3, 'tau2': 6.4, 'e': -80}  # Pi et al 2013
netParams.synMechParams['GABAASlow'] = {'mod': 'MyExp2SynBB','tau1': 2, 'tau2': 100, 'e': -80}
netParams.synMechParams['GABAASlowSlow'] = {'mod': 'MyExp2SynBB', 'tau1': 200, 'tau2': 400, 'e': -80}

ESynMech = ['AMPA', 'NMDA']
SOMESynMech = ['GABAASlow','GABAB']
SOMISynMech = ['GABAASlow']
PVSynMech = ['GABAA']
VIPSynMech = ['GABAA_VIP']
NGFESynMech = ['GABAA', 'GABAB']
NGFISynMech = ['GABAA']
ThalIESynMech = ['GABAASlow','GABAB']
ThalIISynMech = ['GABAASlow']


with open('conn/conn.pkl', 'rb') as fileObj:
    connData = pickle.load(fileObj)
pmat = connData['pmat']
lmat = connData['lmat']
wmat = connData['wmat']
bins = connData['bins']
connDataSource = connData['connDataSource']

preWeights = wmat[prePop]
pop_params_new = {}
for pop in preWeights:
    if preWeights[pop] > 0 and pop in netParams.popParams:
        pop_params_new[pop] = netParams.popParams[pop]
pop_params_new[stimName] = netParams.popParams[stimName]
netParams.popParams = pop_params_new

for post in preWeights:
    if post in netParams.popParams:
        scaleFactor = 1.0
        cellTypeGain = 1.0
        if prePop in Epops:
            synMech = ESynMech
            if post in Epops:
                gain = cfg.EEGain
                popGain = cfg.EEPopGain[post]
                synMechWeightFactor = cfg.synWeightFractionEE
                cell_type = next(k for k in netParams.cellParams if k[:3] == post[:3])
                secs = netParams.cellParams[cell_type]['secs']
            elif post in Ipops:
                popGain = cfg.EIPopGain[post]
                gain = cfg.EIGain
                cell_type = next(k for k in netParams.cellParams if k[:2] == post[:2])
                secs = netParams.cellParams[cell_type]['secs']
                if 'NGF' in post:
                    synMechWeightFactor = cfg.synWeightFractionENGF
                elif 'PV' in post:
                    synMechWeightFactor = cfg.synWeightFractionEI_CustomCort
                else:
                    synMechWeightFactor = cfg.synWeightFractionEI

            netParams.connParams[stimName + '_' + post] = {
                'preConds': {'pop': stimName},
                'postConds': {'pop': post},
                'sec': 'soma',
                'synMech': synMech,
                'weight': preWeights[post] * gain * popGain * scaleFactor,
                'synMechWeightFactor': synMechWeightFactor,
                'synsPerConn': 10,
                'delay': 1000
            }

        elif prePop in Ipops:
            gain = 1.0
            if 'PV' in prePop:
                synMech = PVSynMech
            if 'VIP' in prePop:
                synMech = VIPSynMech
            if post in Ipops:
                synMechWeightFactor = cfg.synWeightFractionII
                gain = cfg.IIGain
                cell_type = next(k for k in netParams.cellParams if k[:2] == post[:2])
                secs = netParams.cellParams[cell_type]['secs']
                if 'SOM' in prePop:
                    synMech = SOMISynMech
                    synMechWeightFactor = cfg.synWeightFractionSOMI
                elif 'NGF' in prePop:
                    synMech = NGFISynMech
                    synMechWeightFactor = cfg.synWeightFractionNGFI
            if post in Epops:
                synMechWeightFactor = cfg.synWeightFractionIE
                gain = cfg.IEGain
                cell_type = next(k for k in netParams.cellParams if k[:3] == post[:3])
                secs = netParams.cellParams[cell_type]['secs']
                if 'SOM' in prePop:
                    synMech = SOMESynMech
                    synMechWeightFactor = cfg.synWeightFractionSOME
                elif 'NGF' in prePop:
                    synMech = NGFESynMech
                    synMechWeightFactor = cfg.synWeightFractionNGFE

            netParams.connParams[stimName + '_' + post] = {
                'preConds': {'pop': stimName},
                'postConds': {'pop': post},
                'sec': 'soma',
                'synMech': synMech,
                'weight': preWeights[post] * gain,
                'synMechWeightFactor': synMechWeightFactor,
                'synsPerConn': 10,
                'delay': 1000
            }

# ------------------------------------------------------------------------------
# Background inputs
# ------------------------------------------------------------------------------

with open('data/bkg_rate_dict.json', 'rb') as f:
    bkg_rates = json.load(f)

desired_rates = {'E': 1.0, 'I': 5.0}

nearest_syns = {}
for pop in bkg_rates:
    rates = bkg_rates[pop]  # dict: syn_num (as str) → firing_rate
    if pop in cfg.Epops:
        target_rate = desired_rates['E']
    else:
        target_rate = desired_rates['I']

    # Find syn_num with firing rate closest to target
    best_syn = min(rates, key=lambda syn: abs(rates[syn] - target_rate))
    nearest_syns[pop] = float(best_syn)

SourcesNumber = 5  # for each post Mtype - sec distribution

synperNeuronStimI = {}
synperNeuronStimE = {}
GsynStimI = {}
GsynStimE = {}

for post in cfg.Ipops + cfg.Epops:
    GsynStimI[post] = 3.0  # PSP = - 1.0 mv if Vrest = - 75 mV
    GsynStimE[post] = 0.45  # PSP = + 1.0 mv if Vrest = - 75 mV

    synperNeuronStimI[post] = 10  # Exc/Inh
    synperNeuronStimE[post] = nearest_syns[post]


if cfg.addBkgConn:
    for post in cfg.Ipops + cfg.Epops:

        synperNeuron = synperNeuronStimI[post]
        ratespontaneous = cfg.rateStimI
        for qSnum in range(SourcesNumber):
            ratesdifferentiation = (0.8 + 0.4*qSnum/(SourcesNumber-1)) * (synperNeuron*ratespontaneous)/SourcesNumber
            netParams.stimSourceParams['StimSyn_all_INH->' + post + '_' + str(qSnum)] = \
                {'type': 'NetStim',
                 'rate': ratesdifferentiation,
                 'noise': 1.0,
                 'start': qSnum*50.0,
                 'number': 1e9}

        synperNeuron = synperNeuronStimE[post]
        ratespontaneous = cfg.rateStimE
        for qSnum in range(SourcesNumber):
            ratesdifferentiation = (0.8 + 0.4*qSnum/(SourcesNumber-1)) * (synperNeuron*ratespontaneous)/SourcesNumber
            netParams.stimSourceParams['StimSyn_all_EXC->' + post + '_' + str(qSnum)] = \
                {'type': 'NetStim',
                 'rate': (0.8 + 0.4*qSnum/(SourcesNumber-1)) * (nearest_syns[post]*ratespontaneous)/SourcesNumber,
                 'noise': 1.0,
                 'start': qSnum*50.0,
                 'number': 1e9}

    # ------------------------------------------------------------------------------
    for post in cfg.Epops:
        for qSnum in range(SourcesNumber):
            netParams.stimTargetParams['StimSyn_all_EXC->' + post + '_' + str(qSnum)] = {
                'source': 'StimSynS1_S_all_EXC->' + post + '_' + str(qSnum),
                'conds':  {'pop': [post]},
                'synMech': 'AMPA',
                'sec': 'all',  # soma not inclued in S1 model
                'weight': GsynStimE[post],
                'delay': 0.1}

    for post in cfg.Ipops:
        for qSnum in range(SourcesNumber):
            netParams.stimTargetParams['StimSyn_all_EXC->' + post + '_' + str(qSnum)] = {
                'source': 'StimSyn_all_EXC->' + post + '_' + str(qSnum),
                'synMech': 'AMPA',
                'conds':  {'pop': [post]},
                'sec': 'all',
                'weight': GsynStimE[post],
                'delay': 0.1}

    for post in cfg.Epops+cfg.Ipops:
        for qSnum in range(SourcesNumber):
            netParams.stimTargetParams['StimSyn_all_INH->' + post + '_' + str(qSnum)] = {
                'source': 'StimSyn_all_INH->' + post + '_' + str(qSnum),
                'conds':  {'pop': [post]},
                'synMech': 'GABAA',
                'sec': 'all',
                'weight': GsynStimI[post],
                'delay': 0.1}
