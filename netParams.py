"""
netParams.py 

High-level specifications for A1 network model using NetPyNE

Contributors: @gmail.com,
"""

from cfg import cfg
from netpyne.batchtools import specs
import pickle
import json
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

try:
    from __main__ import cfg  # import SimConfig object with params from parent module
except:
    from cfg import cfg

# ------------------------------------------------------------------------------
# VERSION
# ------------------------------------------------------------------------------

netParams.version = 0

# ------------------------------------------------------------------------------
#
# NETWORK PARAMETERS
#
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# General network parameters
# ------------------------------------------------------------------------------

netParams.scale = cfg.scale  # Scale factor for number of cells # NOT DEFINED YET! 3/11/19 # How is this different than scaleDensity?
netParams.sizeX = cfg.sizeX  # x-dimension (horizontal length) size in um
netParams.sizeY = cfg.sizeY  # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = cfg.sizeZ  # z-dimension (horizontal depth) size in um
netParams.shape = 'cylinder'  # cylindrical (column-like) volume

# ------------------------------------------------------------------------------
# General connectivity parameters
# -----------------------------------------------------------------------------
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

Etypes = ['IT', 'ITS4', 'PT', 'CT']
Itypes = ['PV', 'SOM', 'VIP', 'NGF']
cellModels = ['HH_reduced', 'HH_full']  # List of cell models

# II: 100-950, IV: 950-1250, V: 1250-1550, VI: 1550-2000
layer = {'1': [0.00, 0.05], '2': [0.05, 0.08], '3': [0.08, 0.475], '4': [0.475, 0.625],
         '5A': [0.625, 0.667], '5B': [0.667, 0.775], '6': [0.775, 1], 'thal': [1.2, 1.4],
         'cochlear': [1.6, 1.601]}  # normalized layer boundaries

layerGroups = {
    '1-3': [layer['1'][0], layer['3'][1]],  # L1-3
    '4': layer['4'],  # L4
    '5': [layer['5A'][0], layer['5B'][1]],  # L5A-5B
    '6': layer['6']}  # L6

# ------------------------------------------------------------------------------
## Load cell rules previously saved using netpyne format (DOES NOT INCLUDE VIP, NGF and spiny stellate)
## include conditions ('conds') for each cellRule
cellParamLabels = ['IT2_reduced', 'IT3_reduced', 'ITP4_reduced', 'ITS4_reduced',
                   'IT5A_reduced', 'CT5A_reduced', 'IT5B_reduced', 'PT5B_reduced',
                   'CT5B_reduced', 'IT6_reduced', 'CT6_reduced', 'PV_reduced',
                   'SOM_reduced', 'VIP_reduced', 'NGF_reduced',
                #    'RE_reduced', 'TC_reduced', 'HTC_reduced', 'TI_reduced',
                   ]

for ruleLabel in cellParamLabels:
    netParams.loadCellParamsRule(label=ruleLabel, fileName='cells/' + ruleLabel + '_cellParams.json')  # Load cellParams for each of the above cell subtype

# ------------------------------------------------------------------------------
# Population parameters
# ------------------------------------------------------------------------------

## load densities
with open('cells/cellDensity.pkl', 'rb') as fileObj:
    density = pickle.load(fileObj)['density']
density = {k: [x * cfg.scaleDensity for x in v] for k, v in density.items()}  # Scale densities

## LAYER 1:
netParams.popParams['NGF1'] = {'cellType': 'NGF', 'cellModel': 'HH_reduced', 'ynormRange': layer['1'], 'density': density[('A1', 'nonVIP')][0]}

## LAYER 2:
netParams.popParams['IT2'] = {'cellType': 'IT', 'cellModel': 'HH_reduced', 'ynormRange': layer['2'], 'density': density[('A1', 'E')][1]}  # cfg.cellmod for 'cellModel' in M1 netParams.py
netParams.popParams['SOM2'] = {'cellType': 'SOM', 'cellModel': 'HH_reduced', 'ynormRange': layer['2'], 'density': density[('A1', 'SOM')][1]}
netParams.popParams['PV2'] = {'cellType': 'PV', 'cellModel': 'HH_reduced', 'ynormRange': layer['2'], 'density': density[('A1', 'PV')][1]}
netParams.popParams['VIP2'] = {'cellType': 'VIP', 'cellModel': 'HH_reduced', 'ynormRange': layer['2'], 'density': density[('A1', 'VIP')][1]}
netParams.popParams['NGF2'] = {'cellType': 'NGF', 'cellModel': 'HH_reduced', 'ynormRange': layer['2'], 'density': density[('A1', 'nonVIP')][1]}

## LAYER 3:
netParams.popParams['IT3'] = {'cellType': 'IT', 'cellModel': 'HH_reduced', 'ynormRange': layer['3'], 'density': density[('A1', 'E')][1]}  # CHANGE DENSITY
netParams.popParams['SOM3'] = {'cellType': 'SOM', 'cellModel': 'HH_reduced', 'ynormRange': layer['3'], 'density': density[('A1', 'SOM')][1]}  # CHANGE DENSITY
netParams.popParams['PV3'] = {'cellType': 'PV', 'cellModel': 'HH_reduced', 'ynormRange': layer['3'], 'density': density[('A1', 'PV')][1]}  # CHANGE DENSITY
netParams.popParams['VIP3'] = {'cellType': 'VIP', 'cellModel': 'HH_reduced', 'ynormRange': layer['3'], 'density': density[('A1', 'VIP')][1]}  # CHANGE DENSITY
netParams.popParams['NGF3'] = {'cellType': 'NGF', 'cellModel': 'HH_reduced', 'ynormRange': layer['3'], 'density': density[('A1', 'nonVIP')][1]}

## LAYER 4:
netParams.popParams['ITP4'] = {'cellType': 'IT', 'cellModel': 'HH_reduced', 'ynormRange': layer['4'], 'density': 0.5 * density[('A1', 'E')][2]}  # CHANGE DENSITY
netParams.popParams['ITS4'] = {'cellType': cfg.ITS4Type, 'cellModel': 'HH_reduced', 'ynormRange': layer['4'], 'density': 0.5 * density[('A1', 'E')][2]}  # CHANGE DENSITY
netParams.popParams['SOM4'] = {'cellType': 'SOM', 'cellModel': 'HH_reduced', 'ynormRange': layer['4'], 'density': density[('A1', 'SOM')][2]}
netParams.popParams['PV4'] = {'cellType': 'PV', 'cellModel': 'HH_reduced', 'ynormRange': layer['4'], 'density': density[('A1', 'PV')][2]}
netParams.popParams['VIP4'] = {'cellType': 'VIP', 'cellModel': 'HH_reduced', 'ynormRange': layer['4'], 'density': density[('A1', 'VIP')][2]}
netParams.popParams['NGF4'] = {'cellType': 'NGF', 'cellModel': 'HH_reduced', 'ynormRange': layer['4'], 'density': density[('A1', 'nonVIP')][2]}

## LAYER 5A:
netParams.popParams['IT5A'] = {'cellType': 'IT', 'cellModel': 'HH_reduced', 'ynormRange': layer['5A'], 'density': 0.5 * density[('A1', 'E')][3]}
netParams.popParams['CT5A'] = {'cellType': 'CT', 'cellModel': 'HH_reduced', 'ynormRange': layer['5A'], 'density': 0.5 * density[('A1', 'E')][3]}
netParams.popParams['SOM5A'] = {'cellType': 'SOM', 'cellModel': 'HH_reduced', 'ynormRange': layer['5A'], 'density': density[('A1', 'SOM')][3]}
netParams.popParams['PV5A'] = {'cellType': 'PV', 'cellModel': 'HH_reduced', 'ynormRange': layer['5A'], 'density': density[('A1', 'PV')][3]}
netParams.popParams['VIP5A'] = {'cellType': 'VIP', 'cellModel': 'HH_reduced', 'ynormRange': layer['5A'], 'density': density[('A1', 'VIP')][3]}
netParams.popParams['NGF5A'] = {'cellType': 'NGF', 'cellModel': 'HH_reduced', 'ynormRange': layer['5A'], 'density': density[('A1', 'nonVIP')][3]}

## LAYER 5B:
netParams.popParams['IT5B'] = {'cellType': 'IT', 'cellModel': 'HH_reduced', 'ynormRange': layer['5B'], 'density': (1 / 3) * density[('A1', 'E')][4]}
netParams.popParams['CT5B'] = {'cellType': 'CT', 'cellModel': 'HH_reduced', 'ynormRange': layer['5B'], 'density': (1 / 3) * density[('A1', 'E')][4]}
netParams.popParams['PT5B'] = {'cellType': 'PT', 'cellModel': 'HH_reduced', 'ynormRange': layer['5B'], 'density': (1 / 3) * density[('A1', 'E')][4]}
netParams.popParams['SOM5B'] = {'cellType': 'SOM', 'cellModel': 'HH_reduced', 'ynormRange': layer['5B'], 'density': density[('A1', 'SOM')][4]}
netParams.popParams['PV5B'] = {'cellType': 'PV', 'cellModel': 'HH_reduced', 'ynormRange': layer['5B'], 'density': density[('A1', 'PV')][4]}
netParams.popParams['VIP5B'] = {'cellType': 'VIP', 'cellModel': 'HH_reduced', 'ynormRange': layer['5B'], 'density': density[('A1', 'VIP')][4]}
netParams.popParams['NGF5B'] = {'cellType': 'NGF', 'cellModel': 'HH_reduced', 'ynormRange': layer['5B'], 'density': density[('A1', 'nonVIP')][4]}

### LAYER 6:
netParams.popParams['IT6'] = {'cellType': 'IT', 'cellModel': 'HH_reduced', 'ynormRange': layer['6'], 'density': 0.5 * density[('A1', 'E')][5]}
netParams.popParams['CT6'] = {'cellType': 'CT', 'cellModel': 'HH_reduced', 'ynormRange': layer['6'], 'density': 0.5 * density[('A1', 'E')][5]}
netParams.popParams['SOM6'] = {'cellType': 'SOM', 'cellModel': 'HH_reduced', 'ynormRange': layer['6'], 'density': density[('A1', 'SOM')][5]}
netParams.popParams['PV6'] = {'cellType': 'PV', 'cellModel': 'HH_reduced', 'ynormRange': layer['6'], 'density': density[('A1', 'PV')][5]}
netParams.popParams['VIP6'] = {'cellType': 'VIP', 'cellModel': 'HH_reduced', 'ynormRange': layer['6'], 'density': density[('A1', 'VIP')][5]}
netParams.popParams['NGF6'] = {'cellType': 'NGF', 'cellModel': 'HH_reduced', 'ynormRange': layer['6'], 'density': density[('A1', 'nonVIP')][5]}

### THALAMIC POPULATIONS (from prev model)
# thalDensity = density[('A1', 'PV')][2] * 1.25  # temporary estimate (from prev model)

# netParams.popParams['TC'] = {'cellType': 'TC', 'cellModel': 'HH_reduced', 'ynormRange': layer['thal'], 'density': 0.75 * thalDensity}
# netParams.popParams['TCM'] = {'cellType': 'TC', 'cellModel': 'HH_reduced', 'ynormRange': layer['thal'], 'density': thalDensity}
# netParams.popParams['HTC'] = {'cellType': 'HTC', 'cellModel': 'HH_reduced', 'ynormRange': layer['thal'], 'density': 0.25 * thalDensity}
# netParams.popParams['IRE'] = {'cellType': 'RE', 'cellModel': 'HH_reduced', 'ynormRange': layer['thal'], 'density': thalDensity}
# netParams.popParams['IREM'] = {'cellType': 'RE', 'cellModel': 'HH_reduced', 'ynormRange': layer['thal'], 'density': thalDensity}
# netParams.popParams['TI'] = {'cellType': 'TI', 'cellModel': 'HH_reduced', 'ynormRange': layer['thal'], 'density': 0.33 * thalDensity}  # Winer & Larue 1996; Huang et al 1999
# netParams.popParams['TIM'] = {'cellType': 'TI', 'cellModel': 'HH_reduced', 'ynormRange': layer['thal'], 'density': 0.33 * thalDensity}  # Winer & Larue 1996; Huang et al 1999

if cfg.singleCellPops:
    for pop in netParams.popParams.values():
        pop['numCells'] = 1

## List of E and I pops to use later on
Epops = ['IT2', 'IT3', 'ITP4', 'ITS4', 'IT5A', 'CT5A', 'IT5B', 'CT5B', 'PT5B', 'IT6', 'CT6']  # all layers

Ipops = ['NGF1',  # L1
         'PV2', 'SOM2', 'VIP2', 'NGF2',  # L2
         'PV3', 'SOM3', 'VIP3', 'NGF3',  # L3
         'PV4', 'SOM4', 'VIP4', 'NGF4',  # L4
         'PV5A', 'SOM5A', 'VIP5A', 'NGF5A',  # L5A
         'PV5B', 'SOM5B', 'VIP5B', 'NGF5B',  # L5B
         'PV6', 'SOM6', 'VIP6', 'NGF6']  # L6

# ------------------------------------------------------------------------------
# Synaptic mechanism parameters
# ------------------------------------------------------------------------------

### From M1 detailed netParams.py
netParams.synMechParams['NMDA'] = {'mod': 'MyExp2SynNMDABB', 'tau1NMDA': 15, 'tau2NMDA': 150, 'e': 0}
netParams.synMechParams['AMPA'] = {'mod': 'MyExp2SynBB', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}
netParams.synMechParams['GABAB'] = {"mod": "MyExp2SynBB", "tau1": 41, "tau2": 642, "e": -105}
netParams.synMechParams['GABAA'] = {'mod': 'MyExp2SynBB', 'tau1': 0.07, 'tau2': 18.2, 'e': -80}
netParams.synMechParams['GABAA_VIP'] = {'mod': 'MyExp2SynBB', 'tau1': 0.3, 'tau2': 6.4, 'e': -80}  # Pi et al 2013
netParams.synMechParams['GABAASlow'] = {'mod': 'MyExp2SynBB', 'tau1': 2, 'tau2': 100, 'e': -80}
netParams.synMechParams['GABAASlowSlow'] = {'mod': 'MyExp2SynBB', 'tau1': 200, 'tau2': 400, 'e': -80}

ESynMech = ['AMPA', 'NMDA']
SOMESynMech = ['GABAASlow', 'GABAB']
SOMISynMech = ['GABAASlow']
PVSynMech = ['GABAA']
VIPSynMech = ['GABAA_VIP']
NGFESynMech = ['GABAA', 'GABAB']
NGFISynMech = ['GABAA']
ThalIESynMech = ['GABAASlow', 'GABAB']
ThalIISynMech = ['GABAASlow']


#------------------------------------------------------------------------------
# IClamp inputs
#------------------------------------------------------------------------------

resting_potential = {}
resting_potential['NGF1'] = -62.60
resting_potential['IT2'] = -85.77
resting_potential['SOM2'] = -64.88
resting_potential['PV2'] = -74.05
resting_potential['VIP2'] = -70.10
resting_potential['NGF2'] = -62.60
resting_potential['IT3'] = -85.67
resting_potential['SOM3'] = -64.88
resting_potential['PV3'] = -74.05
resting_potential['VIP3'] = -70.10
resting_potential['NGF3'] = -62.60
resting_potential['ITP4'] = -85.86
resting_potential['ITS4'] = -85.39
resting_potential['SOM4'] = -64.88
resting_potential['PV4'] = -74.05
resting_potential['VIP4'] = -70.10
resting_potential['NGF4'] = -62.60
resting_potential['IT5A'] = -81.19
resting_potential['CT5A'] = -86.04
resting_potential['SOM5A'] = -64.88
resting_potential['PV5A'] = -74.05
resting_potential['VIP5A'] = -70.10
resting_potential['NGF5A'] = -62.60
resting_potential['IT5B'] = -81.14
resting_potential['CT5B'] = -86.04
resting_potential['PT5B'] = -80.43
resting_potential['SOM5B'] = -64.88
resting_potential['PV5B'] = -74.05
resting_potential['VIP5B'] = -70.10
resting_potential['NGF5B'] = -62.60
resting_potential['IT6'] = -80.50
resting_potential['CT6'] = -86.04
resting_potential['SOM6'] = -64.88
resting_potential['PV6'] = -74.05
resting_potential['VIP6'] = -70.10
resting_potential['NGF6'] = -62.60

input_resistance = {}
input_resistance['NGF1'] = 396.75
input_resistance['IT2'] = 87.13
input_resistance['SOM2'] = 234.53
input_resistance['PV2'] = 140.53
input_resistance['VIP2'] = 227.55
input_resistance['NGF2'] = 396.75
input_resistance['IT3'] = 75.96
input_resistance['SOM3'] = 234.53
input_resistance['PV3'] = 140.53
input_resistance['VIP3'] = 227.55
input_resistance['NGF3'] = 396.75
input_resistance['ITP4'] = 76.21
input_resistance['ITS4'] = 197.72
input_resistance['SOM4'] = 234.53
input_resistance['PV4'] = 140.53
input_resistance['VIP4'] = 227.55
input_resistance['NGF4'] = 396.75
input_resistance['IT5A'] = 115.39
input_resistance['CT5A'] = 57.61
input_resistance['SOM5A'] = 234.53
input_resistance['PV5A'] = 140.53
input_resistance['VIP5A'] = 227.55
input_resistance['NGF5A'] = 396.75
input_resistance['IT5B'] = 107.41
input_resistance['CT5B'] = 57.61
input_resistance['PT5B'] = 71.29
input_resistance['SOM5B'] = 234.53
input_resistance['PV5B'] = 140.53
input_resistance['VIP5B'] = 227.55
input_resistance['NGF5B'] = 396.75
input_resistance['IT6'] = 111.44
input_resistance['CT6'] = 57.61
input_resistance['SOM6'] = 234.53
input_resistance['PV6'] = 140.53
input_resistance['VIP6'] = 227.55
input_resistance['NGF6'] = 396.75

#------------------------------------------------------------------------------
# IClamp
#------------------------------------------------------------------------------
print("%s \t %s \t %s \t %s" % ("popName","resting_potential","input_resistance","holding_current"))
for popName1 in cfg.Ipops + cfg.Epops:

    holding_current1 = (-75.0 - resting_potential[popName1])/input_resistance[popName1]

    print("%s \t %20.3f \t %20.3f \t %20.3f" % (popName1,resting_potential[popName1],input_resistance[popName1],holding_current1))


    netParams.stimSourceParams['Input_'+popName1] = {'type': 'IClamp', 'del': 0.0, 'dur': 10000.0, 'amp': holding_current1}
    netParams.stimTargetParams['Input->'+popName1] = {'source': 'Input_'+popName1, 'sec':'soma_0', 'loc': 0.5, 'conds': {'pop':popName1}}

#------------------------------------------------------------------------------
# NetStim inputs to simulate Spontaneous synapses + background in A1 neurons - data from "   "
#------------------------------------------------------------------------------
SourcesNumber = 5 # for each post Mtype - sec distribution

synperNeuronStimI = {}
synperNeuronStimE = {}
GsynStimI = {}
GsynStimE = {}

for post in cfg.Ipops + cfg.Epops:
    GsynStimI[post] = 3.0  # PSP = - 1.0 mv if Vrest = - 75 mV
    GsynStimE[post] = 0.45 # PSP = + 1.0 mv if Vrest = - 75 mV

    synperNeuronStimI[post] = 10 # Exc/Inh
    synperNeuronStimE[post] = 50 # [1000:10000]

cfg.addStimSynS1 = True
cfg.rateStimI = 5.0  # Hz
cfg.rateStimE = 1.0  # Hz

if cfg.addStimSynS1:
    for post in cfg.Ipops + cfg.Epops:

        synperNeuron = synperNeuronStimI[post]
        ratespontaneous = cfg.rateStimI
        for qSnum in range(SourcesNumber):
            ratesdifferentiation = (0.8 + 0.4*qSnum/(SourcesNumber-1)) * (synperNeuron*ratespontaneous)/SourcesNumber
            netParams.stimSourceParams['StimSynS1_S_all_INH->' + post + '_' + str(qSnum)] = {'type': 'NetStim', 'rate': ratesdifferentiation, 'noise': 1.0, 'start': qSnum*50.0, 'number': 1e9}

        synperNeuron = synperNeuronStimE[post]
        ratespontaneous = cfg.rateStimE
        for qSnum in range(SourcesNumber):
            ratesdifferentiation = (0.8 + 0.4*qSnum/(SourcesNumber-1)) * (synperNeuron*ratespontaneous)/SourcesNumber
            # netParams.stimSourceParams['StimSynS1_S_all_EXC->' + post + '_' + str(qSnum)] = {'type': 'NetStim', 'rate': ratesdifferentiation, 'noise': 1.0, 'start': qSnum*50.0, 'number': 1e9}
            netParams.stimSourceParams['StimSynS1_S_all_EXC->' + post + '_' + str(qSnum)] = {'type': 'NetStim', 'rate': (0.8 + 0.4*qSnum/(SourcesNumber-1)) * (cfg.background_Exc*ratespontaneous)/SourcesNumber, 'noise': 1.0, 'start': qSnum*50.0, 'number': 1e9}

    #------------------------------------------------------------------------------
    for post in cfg.Epops:
        for qSnum in range(SourcesNumber):
            netParams.stimTargetParams['StimSynS1_T_all_EXC->' + post + '_' + str(qSnum)] = {
                'source': 'StimSynS1_S_all_EXC->' + post + '_' + str(qSnum),
                'conds':  {'pop': [post]},
                'synMech': 'AMPA',
                'sec': 'all',  # soma not inclued in S1 model
                'weight': GsynStimE[post],
                'delay': 0.1}

    for post in cfg.Ipops:
        for qSnum in range(SourcesNumber):
            netParams.stimTargetParams['StimSynS1_T_all_EXC->' + post + '_' + str(qSnum)] = {
                'source': 'StimSynS1_S_all_EXC->' + post + '_' + str(qSnum),
                'synMech': 'AMPA',
                'conds':  {'pop': [post]},
                'sec': 'all',
                'weight': GsynStimE[post],
                'delay': 0.1}

    for post in cfg.Epops+cfg.Ipops:
        for qSnum in range(SourcesNumber):
            netParams.stimTargetParams['StimSynS1_T_all_INH->' + post + '_' + str(qSnum)] = {
                'source': 'StimSynS1_S_all_INH->' + post + '_' + str(qSnum),
                'conds':  {'pop': [post]},
                'synMech': 'GABAA',
                'sec': 'all',
                'weight': GsynStimI[post],
                'delay': 0.1}






# ------------------------------------------------------------------------------
# Description
# ------------------------------------------------------------------------------

netParams.description = """
v0 - 
"""
