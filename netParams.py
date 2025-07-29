"""
netParams.py 

High-level specifications for A1 network model using NetPyNE

Contributors: ericaygriffith@gmail.com, salvadordura@gmail.com, samnemo@gmail.com , & Christoph Metzner
"""

from cfg import cfg
from netpyne.batchtools import specs
import pickle
import json

netParams = specs.NetParams()  # object of class NetParams to store the network parameters

# ------------------------------------------------------------------------------
# VERSION
# ------------------------------------------------------------------------------

netParams.version = 45

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
                   'SOM_reduced', 'VIP_reduced', 'NGF_reduced', 'RE_reduced',
                   'TC_reduced', 'HTC_reduced', 'TI_reduced']

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
thalDensity = density[('A1', 'PV')][2] * 1.25  # temporary estimate (from prev model)

netParams.popParams['TC'] = {'cellType': 'TC', 'cellModel': 'HH_reduced', 'ynormRange': layer['thal'], 'density': 0.75 * thalDensity}
netParams.popParams['TCM'] = {'cellType': 'TC', 'cellModel': 'HH_reduced', 'ynormRange': layer['thal'], 'density': thalDensity}
netParams.popParams['HTC'] = {'cellType': 'HTC', 'cellModel': 'HH_reduced', 'ynormRange': layer['thal'], 'density': 0.25 * thalDensity}
netParams.popParams['IRE'] = {'cellType': 'RE', 'cellModel': 'HH_reduced', 'ynormRange': layer['thal'], 'density': thalDensity}
netParams.popParams['IREM'] = {'cellType': 'RE', 'cellModel': 'HH_reduced', 'ynormRange': layer['thal'], 'density': thalDensity}
netParams.popParams['TI'] = {'cellType': 'TI', 'cellModel': 'HH_reduced', 'ynormRange': layer['thal'], 'density': 0.33 * thalDensity}  # Winer & Larue 1996; Huang et al 1999
netParams.popParams['TIM'] = {'cellType': 'TI', 'cellModel': 'HH_reduced', 'ynormRange': layer['thal'], 'density': 0.33 * thalDensity}  # Winer & Larue 1996; Huang et al 1999

if cfg.singleCellPops:
    for pop in netParams.popParams.values():
        pop['numCells'] = 1

if cfg.reducedPop:
    for pop in netParams.popParams.values():
        pop['numCells'] = cfg.reducedPop

## List of E and I pops to use later on
Epops = ['IT2', 'IT3', 'ITP4', 'ITS4', 'IT5A', 'CT5A', 'IT5B', 'CT5B', 'PT5B', 'IT6', 'CT6']  # all layers

Ipops = ['NGF1',  # L1
         'PV2', 'SOM2', 'VIP2', 'NGF2',  # L2
         'PV3', 'SOM3', 'VIP3', 'NGF3',  # L3
         'PV4', 'SOM4', 'VIP4', 'NGF4',  # L4
         'PV5A', 'SOM5A', 'VIP5A', 'NGF5A',  # L5A
         'PV5B', 'SOM5B', 'VIP5B', 'NGF5B',  # L5B
         'PV6', 'SOM6', 'VIP6', 'NGF6']  # L6

if hasattr(cfg, 'pops_active') and cfg.pops_active:
    pop_params_new = {}
    for pop in cfg.pops_active:
        if pop in netParams.popParams:
            pop_params_new[pop] = netParams.popParams[pop]
        else:
            print(f"Warning: pop '{pop}' not found in netParams.popParams")
    netParams.popParams = pop_params_new

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

# ------------------------------------------------------------------------------
# Local connectivity parameters
# ------------------------------------------------------------------------------

## load data from conn pre-processing file
with open('conn/conn.pkl', 'rb') as fileObj:
    connData = pickle.load(fileObj)
pmat = connData['pmat']
lmat = connData['lmat']
wmat = connData['wmat']
bins = connData['bins']
connDataSource = connData['connDataSource']

wmat = cfg.wmat

layerGainLabels = ['1', '2', '3', '4', '5A', '5B', '6']


def wireCortex():
    # ------------------------------------------------------------------------------
    ## E -> E
    if cfg.EEGain > 0.0:
        for pre in Epops:
            for post in Epops:
                for l in layerGainLabels:  # used to tune each layer group independently
                    scaleFactor = 1.0
                    if connDataSource['E->E/I'] in ['Allen_V1', 'Allen_custom']:
                        prob = '%f * exp(-dist_2D/%f)' % (pmat[pre][post], lmat[pre][post])
                    else:
                        prob = pmat[pre][post]
                    if post == 'CT6':
                        scaleFactor = cfg.CT6ScaleFactor
                    if pre == 'ITS4' or pre == 'ITP4':
                        if post == 'IT3':
                            scaleFactor = cfg.L4L3E  # 25
                        if post == 'ITP4' or post == 'ITS4':
                            scaleFactor = cfg.L4L4E

                    netParams.connParams['EE_' + pre + '_' + post + '_' + l] = {
                        'preConds': {'pop': pre},
                        'postConds': {'pop': post, 'ynorm': layer[l]},
                        'synMech': ESynMech,
                        'probability': prob,
                        'weight': wmat[pre][post] * cfg.EEGain * cfg.EELayerGain[l] * cfg.EEPopGain[post] * scaleFactor,
                        'synMechWeightFactor': cfg.synWeightFractionEE,
                        'delay': 'defaultDelay+dist_3D/propVelocity',
                        'synsPerConn': 1,
                        'sec': 'dend_all'}
    # ------------------------------------------------------------------------------
    ## E -> I       ## MODIFIED FOR NMDAR MANIPULATION!!
    if cfg.EIGain > 0.0:
        for pre in Epops:
            for post in Ipops:
                for postType in Itypes:
                    if postType in post:  # only create rule if celltype matches pop
                        for l in layerGainLabels:  # used to tune each layer group independently
                            scaleFactor = 1.0
                            if connDataSource['E->E/I'] in ['Allen_V1', 'Allen_custom']:
                                prob = '%f * exp(-dist_2D/%f)' % (pmat[pre][post], lmat[pre][post])
                            else:
                                prob = pmat[pre][post]
                            if 'NGF' in post:
                                synWeightFactor = cfg.synWeightFractionENGF
                            elif 'PV' in post:
                                synWeightFactor = cfg.synWeightFractionEI_CustomCort
                            else:
                                synWeightFactor = cfg.synWeightFractionEI  # cfg.synWeightFractionEI_CustomCort  #cfg.synWeightFractionEI
                            if 'NGF1' in post:
                                scaleFactor = cfg.ENGF1
                            if pre == 'IT3':
                                if post == 'IT3':
                                    scaleFactor = cfg.L3L3scaleFactor
                                if post == 'PV4':
                                    scaleFactor = cfg.L3L4PV
                                elif post == 'SOM4':
                                    scaleFactor = cfg.L3L4SOM
                            if pre == 'ITS4' or pre == 'ITP4':
                                if post == 'PV3':
                                    scaleFactor = cfg.L4L3PV  # 25
                                elif post == 'SOM3':
                                    scaleFactor = cfg.L4L3SOM
                                elif post == 'NGF3':
                                    scaleFactor = cfg.L4L3NGF  # 25
                                elif post == 'VIP3':
                                    scaleFactor = cfg.L4L3VIP  # 25
                            netParams.connParams['EI_' + pre + '_' + post + '_' + postType + '_' + l] = {
                                'preConds': {'pop': pre},
                                'postConds': {'pop': post, 'cellType': postType, 'ynorm': layer[l]},
                                'synMech': ESynMech,
                                'probability': prob,
                                'weight': wmat[pre][post] * cfg.EIGain * cfg.EICellTypeGain[postType] * cfg.EILayerGain[
                                    l] * cfg.EIPopGain[post] * scaleFactor,
                                'synMechWeightFactor': synWeightFactor,
                                'delay': 'defaultDelay+dist_3D/propVelocity',
                                'synsPerConn': 1,
                                'sec': 'proximal'}
    # cfg.NMDARfactor * wmat[pre][post] * cfg.EIGain * cfg.EICellTypeGain[postType] * cfg.EILayerGain[l]]
    # ------------------------------------------------------------------------------
    ## I -> E
    if cfg.IEGain > 0.0:
        if connDataSource['I->E/I'] == 'Allen_custom':
            for pre in Ipops:
                for preType in Itypes:
                    if preType in pre:  # only create rule if celltype matches pop
                        for post in Epops:
                            for l in layerGainLabels:  # used to tune each layer group independently
                                prob = '%f * exp(-dist_2D/%f)' % (pmat[pre][post], lmat[pre][post])
                                synWeightFactor = cfg.synWeightFractionIE
                                if 'SOM' in pre:
                                    synMech = SOMESynMech
                                    synWeightFactor = cfg.synWeightFractionSOME
                                elif 'PV' in pre:
                                    synMech = PVSynMech
                                elif 'VIP' in pre:
                                    synMech = VIPSynMech
                                elif 'NGF' in pre:
                                    synMech = NGFESynMech
                                    synWeightFactor = cfg.synWeightFractionNGFE
                                netParams.connParams['IE_' + pre + '_' + preType + '_' + post + '_' + l] = {
                                    'preConds': {'pop': pre},
                                    'postConds': {'pop': post, 'ynorm': layer[l]},
                                    'synMech': synMech,
                                    'probability': prob,
                                    'weight': wmat[pre][post] * cfg.IEGain * cfg.IECellTypeGain[preType] * cfg.IELayerGain[l],
                                    'synMechWeightFactor': synWeightFactor,
                                    'delay': 'defaultDelay+dist_3D/propVelocity',
                                    'synsPerConn': 1,
                                    'sec': 'proximal'}
    # ------------------------------------------------------------------------------
    ## I -> I
    if cfg.IIGain > 0.0:
        if connDataSource['I->E/I'] == 'Allen_custom':
            for pre in Ipops:
                for post in Ipops:
                    for l in layerGainLabels:
                        prob = '%f * exp(-dist_2D/%f)' % (pmat[pre][post], lmat[pre][post])
                        synWeightFactor = cfg.synWeightFractionII
                        if 'SOM' in pre:
                            synMech = SOMISynMech
                            synWeightFactor = cfg.synWeightFractionSOMI
                        elif 'PV' in pre:
                            synMech = PVSynMech
                        elif 'VIP' in pre:
                            synMech = VIPSynMech
                        elif 'NGF' in pre:
                            synMech = NGFISynMech
                            synWeightFactor = cfg.synWeightFractionNGFI
                        netParams.connParams['II_' + pre + '_' + post + '_' + l] = {
                            'preConds': {'pop': pre},
                            'postConds': {'pop': post, 'ynorm': layer[l]},
                            'synMech': synMech,
                            'probability': prob,
                            'weight': wmat[pre][post] * cfg.IIGain * cfg.IILayerGain[l],
                            'synMechWeightFactor': synWeightFactor,
                            'delay': 'defaultDelay+dist_3D/propVelocity',
                            'synsPerConn': 1,
                            'sec': 'proximal'}


if cfg.addConn and cfg.wireCortex:
    print('wiring ctx')
    wireCortex()

# ------------------------------------------------------------------------------
# Thalamic connectivity parameters
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
## Intrathalamic

TEpops = ['TC', 'TCM', 'HTC']
TIpops = ['IRE', 'IREM', 'TI', 'TIM']


def IsThalamicCore(ct):
    return ct == 'TC' or ct == 'HTC' or ct == 'IRE' or ct == 'TI'


def wireThal():
    # set intrathalamic connections
    for pre in TEpops + TIpops:
        for post in TEpops + TIpops:
            gain = cfg.intraThalamicGain
            if post in pmat[pre]:
                # for syns use ESynMech, ThalIESynMech and ThalIISynMech
                if pre in TEpops:  # E->E/I
                    syn = ESynMech
                    synWeightFactor = cfg.synWeightFractionEE
                    if post in TEpops:
                        gain *= cfg.intraThalamicEEGain
                    else:
                        gain = cfg.intraThalamicEIGain
                elif post in TEpops:  # I->E
                    syn = ThalIESynMech
                    synWeightFactor = cfg.synWeightFractionThalIE
                    gain *= cfg.intraThalamicIEGain
                else:  # I->I
                    syn = ThalIISynMech
                    synWeightFactor = cfg.synWeightFractionThalII
                    gain *= cfg.intraThalamicIIGain
                # use spatially dependent wiring between thalamic core excitatory neurons
                if (pre == 'TC' and (post == 'TC' or post == 'HTC')) or (pre == 'HTC' and (post == 'TC' or post == 'HTC')):
                    prob = '%f * exp(-dist_x/%f)' % (pmat[pre][post], ThalamicCoreLambda)
                else:
                    prob = pmat[pre][post]
                netParams.connParams['ITh_' + pre + '_' + post] = {
                    'preConds': {'pop': pre},
                    'postConds': {'pop': post},
                    'synMech': syn,
                    'probability': prob,
                    'weight': wmat[pre][post] * gain,
                    'synMechWeightFactor': synWeightFactor,
                    'delay': 'defaultDelay+dist_3D/propVelocity',
                    'synsPerConn': 1,
                    'sec': 'soma'}


if cfg.addConn and cfg.addIntraThalamicConn:
    print('adding intrathal')
    wireThal()


# ------------------------------------------------------------------------------
## Corticothalamic


def connectCortexToThal():
    for pre in Epops:
        for post in TEpops + TIpops:
            if post in pmat[pre]:
                if IsThalamicCore(post):  # use spatially dependent wiring for thalamic core
                    prob = '%f * exp(-dist_x/%f)' % (pmat[pre][post], ThalamicCoreLambda)
                else:
                    prob = pmat[pre][post]
                if post in TIpops:
                    CTGain = cfg.CTGainThalI
                else:
                    CTGain = cfg.corticoThalamicGain
                netParams.connParams['CxTh_' + pre + '_' + post] = {
                    'preConds': {'pop': pre},
                    'postConds': {'pop': post},
                    'synMech': ESynMech,
                    'probability': prob,
                    'weight': wmat[pre][post] * CTGain,
                    'synMechWeightFactor': cfg.synWeightFractionEE,
                    'delay': 'defaultDelay+dist_3D/propVelocity',
                    'synsPerConn': 1,
                    'sec': 'soma'}


if cfg.addConn and cfg.addCorticoThalamicConn:
    connectCortexToThal()


# ------------------------------------------------------------------------------
## Thalamocortical - this was added from Christoph Metzner's branch


def connectThalToCortex():
    # thalamocortical connections, some params added from Christoph Metzner's branch
    for pre in TEpops + TIpops:
        for post in Epops + Ipops:
            scaleFactor = 1.0
            if post in pmat[pre]:
                if IsThalamicCore(pre):  # use spatially dependent wiring for thalamic core
                    # NB: should check if this is ok
                    prob = '%f * exp(-dist_x/%f)' % (pmat[pre][post], ThalamicCoreLambda)
                else:
                    # NB: check what the 2D inverse distance based on. lmat from conn/conn.pkl
                    prob = '%f * exp(-dist_2D/%f)' % (pmat[pre][post], lmat[pre][post])
                # for syns use ESynMech, SOMESynMech and SOMISynMech
                if pre in TEpops:  # E->E/I
                    if post == 'PV4':
                        syn = ESynMech
                        synWeightFactor = cfg.synWeightFractionEE
                        scaleFactor = cfg.thalL4PV  # 25
                    elif post == 'SOM4':
                        syn = ESynMech
                        synWeightFactor = cfg.synWeightFractionEE
                        scaleFactor = cfg.thalL4SOM
                    elif post == 'ITS4':
                        syn = ESynMech
                        synWeightFactor = cfg.synWeightFractionEE
                        scaleFactor = cfg.thalL4E  # 25
                    elif post == 'ITP4':
                        syn = ESynMech
                        synWeightFactor = cfg.synWeightFractionEE
                        scaleFactor = cfg.thalL4E  # 25
                    elif post == 'NGF4':
                        syn = ESynMech
                        synWeightFactor = cfg.synWeightFractionEE
                        scaleFactor = cfg.thalL4NGF  # 25
                    elif post == 'VIP4':
                        syn = ESynMech
                        synWeightFactor = cfg.synWeightFractionEE
                        scaleFactor = cfg.thalL4VIP  # 25
                    elif post == 'NGF1':
                        syn = ESynMech
                        synWeightFactor = cfg.synWeightFractionEE
                        scaleFactor = cfg.thalL1NGF  # 25
                    else:
                        syn = ESynMech
                        synWeightFactor = cfg.synWeightFractionEE
                elif post in Epops:  # I->E
                    syn = ThalIESynMech
                    synWeightFactor = cfg.synWeightFractionThalCtxIE
                else:  # I->I
                    syn = ThalIISynMech
                    synWeightFactor = cfg.synWeightFractionThalCtxII

                netParams.connParams['ThCx_' + pre + '_' + post] = {
                    'preConds': {'pop': pre},
                    'postConds': {'pop': post},
                    'synMech': syn,
                    'probability': prob,
                    'weight': wmat[pre][post] * cfg.thalamoCorticalGain * scaleFactor,
                    'synMechWeightFactor': synWeightFactor,
                    'delay': 'defaultDelay+dist_3D/propVelocity',
                    'synsPerConn': 1,
                    'sec': 'soma'}


if cfg.addConn and cfg.addThalamoCorticalConn:
    connectThalToCortex()


# ------------------------------------------------------------------------------
# Subcellular connectivity (synaptic distributions)
# ------------------------------------------------------------------------------

# Set target sections (somatodendritic distribution of synapses)
# From Billeh 2019 (Allen V1) (fig 4F) and Tremblay 2016 (fig 3)

# ------------------------------------------------------------------------------
# Subcellular connectivity (synaptic distributions)
# ------------------------------------------------------------------------------
# Set target sections (somatodendritic distribution of synapses)
# From Billeh 2019 (Allen V1) (fig 4F) and Tremblay 2016 (fig 3)


def addSubConn():
    # ------------------------------------------------------------------------------
    # E -> E2/3,4: soma,dendrites <200um
    netParams.subConnParams['E->E2,3,4'] = {
        'preConds': {'cellType': ['IT', 'ITS4', 'PT', 'CT']},
        'postConds': {'pop': ['IT2', 'IT3', 'ITP4', 'ITS4']},
        'sec': 'proximal',
        'groupSynMechs': ESynMech,
        'density': 'uniform'}
    # ------------------------------------------------------------------------------
    # E -> E5,6: soma,dendrites (all)
    netParams.subConnParams['E->E5,6'] = {
        'preConds': {'cellType': ['IT', 'ITS4', 'PT', 'CT']},
        'postConds': {'pop': ['IT5A', 'CT5A', 'IT5B', 'PT5B', 'CT5B', 'IT6', 'CT6']},
        'sec': 'all',
        'groupSynMechs': ESynMech,
        'density': 'uniform'}
    # ------------------------------------------------------------------------------
    # E -> I: soma, dendrite (all)
    netParams.subConnParams['E->I'] = {
        'preConds': {'cellType': ['IT', 'ITS4', 'PT', 'CT']},
        'postConds': {'cellType': ['PV', 'SOM', 'NGF', 'VIP']},
        'sec': 'all',
        'groupSynMechs': ESynMech,
        'density': 'uniform'}
    # ------------------------------------------------------------------------------
    # NGF1 -> E: apic_tuft
    netParams.subConnParams['NGF1->E'] = {
        'preConds': {'pop': ['NGF1']},
        'postConds': {'cellType': ['IT', 'ITS4', 'PT', 'CT']},
        'sec': 'apic_tuft',
        'groupSynMechs': NGFESynMech,
        'density': 'uniform'}
    # ------------------------------------------------------------------------------
    # NGF2,3,4 -> E2,3,4: apic_trunk
    netParams.subConnParams['NGF2,3,4->E2,3,4'] = {
        'preConds': {'pop': ['NGF2', 'NGF3', 'NGF4']},
        'postConds': {'pop': ['IT2', 'IT3', 'ITP4', 'ITS4']},
        'sec': 'apic_trunk',
        'groupSynMechs': NGFESynMech,
        'density': 'uniform'}
    # ------------------------------------------------------------------------------
    # NGF2,3,4 -> E5,6: apic_uppertrunk
    netParams.subConnParams['NGF2,3,4->E5,6'] = {
        'preConds': {'pop': ['NGF2', 'NGF3', 'NGF4']},
        'postConds': {'pop': ['IT5A', 'CT5A', 'IT5B', 'PT5B', 'CT5B', 'IT6', 'CT6']},
        'sec': 'apic_uppertrunk',
        'groupSynMechs': NGFESynMech,
        'density': 'uniform'}
    # ------------------------------------------------------------------------------
    # NGF5,6 -> E5,6: apic_lowerrunk
    netParams.subConnParams['NGF5,6->E5,6'] = {
        'preConds': {'pop': ['NGF5A', 'NGF5B', 'NGF6']},
        'postConds': {'pop': ['IT5A', 'CT5A', 'IT5B', 'PT5B', 'CT5B', 'IT6', 'CT6']},
        'sec': 'apic_lowertrunk',
        'groupSynMechs': NGFESynMech,
        'density': 'uniform'}
    # ------------------------------------------------------------------------------
    #  SOM -> E: all_dend (not close to soma)
    netParams.subConnParams['SOM->E'] = {
        'preConds': {'cellType': ['SOM']},
        'postConds': {'cellType': ['IT', 'ITS4', 'PT', 'CT']},
        'sec': 'dend_all',
        'groupSynMechs': SOMESynMech,
        'density': 'uniform'}
    # ------------------------------------------------------------------------------
    #  PV -> E: proximal
    netParams.subConnParams['PV->E'] = {
        'preConds': {'cellType': ['PV']},
        'postConds': {'cellType': ['IT', 'ITS4', 'PT', 'CT']},
        'sec': 'proximal',
        'groupSynMechs': PVSynMech,
        'density': 'uniform'}
    # ------------------------------------------------------------------------------
    #  TC -> E: proximal
    netParams.subConnParams['TC->E'] = {
        'preConds': {'cellType': ['TC', 'HTC']},
        'postConds': {'cellType': ['IT', 'ITS4', 'PT', 'CT']},
        'sec': 'proximal',
        'groupSynMechs': ESynMech,
        'density': 'uniform'}
    # ------------------------------------------------------------------------------
    #  TCM -> E: apical
    netParams.subConnParams['TCM->E'] = {
        'preConds': {'cellType': ['TCM']},
        'postConds': {'cellType': ['IT', 'ITS4', 'PT', 'CT']},
        'sec': 'apic',
        'groupSynMechs': ESynMech,
        'density': 'uniform'}


if cfg.addSubConn:
    addSubConn()

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
            # netParams.stimSourceParams['StimSynS1_S_all_EXC->' + post + '_' + str(qSnum)] = {'type': 'NetStim', 'rate': ratesdifferentiation, 'noise': 1.0, 'start': qSnum*50.0, 'number': 1e9}
            netParams.stimSourceParams['StimSyn_all_EXC->' + post + '_' + str(qSnum)] = \
                {'type': 'NetStim',
                 'rate': (0.8 + 0.4*qSnum/(SourcesNumber-1)) * (nearest_syns[post]*ratespontaneous)/SourcesNumber,
                 'noise': 1.0,
                 'start': qSnum*50.0,
                 'number': 1e9}

    # ------------------------------------------------------------------------------
    for post in cfg.Epops:
        for qSnum in range(SourcesNumber):
            netParams.stimTargetParams['StimSyn_T_all_EXC->' + post + '_' + str(qSnum)] = {
                'source': 'StimSynS1_S_all_EXC->' + post + '_' + str(qSnum),
                'conds':  {'pop': [post]},
                'synMech': 'AMPA',
                'sec': 'all',  # soma not inclued in S1 model
                'weight': GsynStimE[post],
                'delay': 0.1}

    for post in cfg.Ipops:
        for qSnum in range(SourcesNumber):
            netParams.stimTargetParams['StimSyn_T_all_EXC->' + post + '_' + str(qSnum)] = {
                'source': 'StimSyn_all_EXC->' + post + '_' + str(qSnum),
                'synMech': 'AMPA',
                'conds':  {'pop': [post]},
                'sec': 'all',
                'weight': GsynStimE[post],
                'delay': 0.1}

    for post in cfg.Epops+cfg.Ipops:
        for qSnum in range(SourcesNumber):
            netParams.stimTargetParams['StimSyn6_T_all_INH->' + post + '_' + str(qSnum)] = {
                'source': 'StimSyn_all_INH->' + post + '_' + str(qSnum),
                'conds':  {'pop': [post]},
                'synMech': 'GABAA',
                'sec': 'all',
                'weight': GsynStimI[post],
                'delay': 0.1}


def prob2conv(prob, npre):
    # probability to convergence; prob is connection probability, npre is number of presynaptic neurons
    return int(0.5 + prob * npre)


# cochlea -> thal
def connectCochleaToThal():
    prob = '%f * exp(-dist_x/%f)' % (cfg.cochlearThalInput['probECore'], ThalamicCoreLambda)
    netParams.connParams['cochlea->ThalECore'] = {
        'preConds': {'pop': 'cochlea'},
        'postConds': {'pop': ['TC', 'HTC']},
        'sec': 'soma',
        'loc': 0.5,
        'synMech': ESynMech,
        'probability': prob,
        'weight': cfg.cochlearThalInput['weightECore'],
        'synMechWeightFactor': cfg.synWeightFractionEE,
        'delay': cfg.delayBkg}
    prob = '%f * exp(-dist_x/%f)' % (cfg.cochlearThalInput['probICore'], ThalamicCoreLambda)
    netParams.connParams['cochlea->ThalICore'] = {
        'preConds': {'pop': 'cochlea'},
        'postConds': {'pop': ['TI']},  # 'IRE',
        'sec': 'soma',
        'loc': 0.5,
        'synMech': ESynMech,
        'probability': prob,
        'weight': cfg.cochlearThalInput['weightICore'],
        'synMechWeightFactor': cfg.synWeightFractionEI,
        'delay': cfg.delayBkg}
    # cochlea -> Thal Matrix
    netParams.connParams['cochlea->ThalEMatrix'] = {
        'preConds': {'pop': 'cochlea'},
        'postConds': {'pop': 'TCM'},
        'sec': 'soma',
        'loc': 0.5,
        'synMech': ESynMech,
        'convergence': prob2conv(cfg.cochlearThalInput['probEMatrix'], numCochlearCells),
        'weight': cfg.cochlearThalInput['weightEMatrix'],
        'synMechWeightFactor': cfg.synWeightFractionEE,
        'delay': cfg.delayBkg}
    netParams.connParams['cochlea->ThalIMatrix'] = {
        'preConds': {'pop': 'cochlea'},
        'postConds': {'pop': ['TIM']},  # 'IREM',
        'sec': 'soma',
        'loc': 0.5,
        'synMech': ESynMech,
        'convergence': prob2conv(cfg.cochlearThalInput['probIMatrix'], numCochlearCells),
        'weight': cfg.cochlearThalInput['weightIMatrix'],
        'synMechWeightFactor': cfg.synWeightFractionEI,
        'delay': cfg.delayBkg}


if cfg.cochlearThalInput:
    from input import cochlearSpikes

    dcoch = cochlearSpikes(freqRange=cfg.cochlearThalInput['freqRange'],
                           numCenterFreqs=cfg.cochlearThalInput['numCenterFreqs'],
                           loudnessScale=cfg.cochlearThalInput['loudnessScale'],
                           lfnwave=cfg.cochlearThalInput['lfnwave'],
                           lonset=cfg.cochlearThalInput['lonset'])
    cochlearSpkTimes = dcoch['spkT']
    cochlearCenterFreqs = dcoch['cf']
    netParams.cf = dcoch['cf']
    numCochlearCells = len(cochlearCenterFreqs)
    netParams.popParams['cochlea'] = {
        'cellModel': 'VecStim',
        'numCells': numCochlearCells,
        'spkTimes': cochlearSpkTimes,
        'ynormRange': layer['cochlear']}

    connectCochleaToThal()

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

# ------------------------------------------------------------------------------
# IClamp
# ------------------------------------------------------------------------------
print("%s \t %s \t %s \t %s" % ("popName","resting_potential","input_resistance","holding_current"))
for popName in cfg.Ipops + cfg.Epops:

    holding_current = (-75.0 - resting_potential[popName])/input_resistance[popName]

    print("%s \t %20.3f \t %20.3f \t %20.3f" % (popName,resting_potential[popName],input_resistance[popName],holding_current))


    netParams.stimSourceParams['Input_'+popName] = {
        'type': 'IClamp', 
        'del': 0.0, 
        'dur': cfg.duration, 
        'amp': holding_current}
        
    netParams.stimTargetParams['Input->'+popName] = {
        'source': 
        'Input_'+popName, 
        'sec':'soma', 
        'loc': 0.5, 
        'conds': {'pop':popName}}


if cfg.addIClamp:
    if cfg.addIClamp['FIcurve']:
        for i in range(cfg.addIClamp['numInjections']):
            start_time = i * cfg.addIClamp['injectionInterval']
            amp = cfg.addIClamp['injectionAmplitudes'][i]
            key = f'IClamp_{i}'

            # Add stim source
            netParams.stimSourceParams[key] = {
                'type': 'IClamp',
                'delay': start_time,
                'dur': cfg.addIClamp['injectionDuration'],
                'amp': amp
            }

            # Connect stim source to all cells
            for pop in cfg.allpops:
                netParams.stimTargetParams[f'{key}_{pop}'] = {
                    'source': key,
                    'conds': {'pop': pop},
                    'sec': 'soma',  # Assuming you want to inject current into the soma
                    'loc': 0.5
                }

    if cfg.addIClamp['holdingCurrent']:
        for pop in cfg.addIClamp['includePops']:
            key = f'IClamp_holding_{pop}'

            netParams.stimSourceParams[key] = {
                'type': 'IClamp',
                'delay': cfg.addIClamp['hold_delay'],
                'dur': cfg.addIClamp['hold_duration'],
                'amp': cfg.addIClamp['holdingAmp']
            }

            netParams.stimTargetParams[key] = {
                'source': key,
                'conds': {'pop': pop},
                'sec': 'soma',
                'loc': 0.5
            }

if cfg.addNoiseConductance:
    with open('data/inputResistances.json', 'rb') as f:
    # with open('simOutput/input_res_0/input_res_vals.json', 'rb') as f:
        inpRes = json.load(f)

    netParams.NoiseConductanceParams = {}
    for pop in cfg.allpops:
        Gin = 1 / inpRes[pop]
        g0 = (cfg.OUamp / 100) * Gin
        sigma = (cfg.OUstd / 100) * Gin
        # print('pop is: '  + pop + ' Input resistance is: ' + str(inpRes[pop]) + ' input conductance is: ' + str(Gin) + '   g0 is:  ' + str(g0))
        netParams.NoiseConductanceParams[pop] = {
            'g0': g0,
            'sigma': sigma
        }

        for pop in cfg.allpops:
            netParams.stimSourceParams['NoiseSEClamp_source_' + pop] = {
                'type': 'ConductanceSource',
                'dur1': cfg.NoiseConductanceDur,
                'amp1': 0  # rmpPops[pop] #abs(rmpPops[pop] * 0.18)
            }
            netParams.stimTargetParams['NoiseSEClamp_target_' + pop] = {
                'source': 'NoiseSEClamp_source_' + pop,
                'sec': 'soma',
                'loc': 0.5,
                'conds': {'pop': pop}
            }

if cfg.addNoiseIClamp:
    with open('data/inputResistances.json', 'rb') as f:
        inpRes = json.load(f)

    netParams.NoiseIClampParams = {}
    for pop in cfg.allpops:
        Gin = 1 / inpRes[pop]
        g0 = (cfg.OUamp / 100) * Gin
        sigma = (cfg.OUstd / 100) * Gin
        # print('pop is: '  + pop + ' Input resistance is: ' + str(inpRes[pop]) + ' input conductance is: ' + str(Gin) + '   g0 is:  ' + str(g0))
        netParams.NoiseIClampParams[pop] = {
            'g0': g0,
            'sigma': sigma
        }

    for pop in cfg.allpops:
        netParams.stimSourceParams['NoiseIClamp_source_' + pop] = {
            'type': 'IClamp',
            'dur': cfg.NoiseConductanceDur,
            'amp': 0  # rmpPops[pop] #abs(rmpPops[pop] * 0.18)
        }
        netParams.stimTargetParams['NoiseIClamp_target_' + pop] = {
            'source': 'NoiseIClamp_source_' + pop,
            'sec': 'soma',
            'loc': 0.5,
            'conds': {'pop': pop}
        }

# ------------------------------------------------------------------------------
# NetStim inputs (to simulate short external stimuli; not bkg)
# ------------------------------------------------------------------------------
if cfg.addNetStim:
    for key in [k for k in dir(cfg) if k.startswith('NetStim')]:
        params = getattr(cfg, key, None)
        [pop, ynorm, sec, loc, synMech, synMechWeightFactor, start, interval, noise, number, weight, delay] = \
            [params[s] for s in ['pop', 'ynorm', 'sec', 'loc', 'synMech', 'synMechWeightFactor', 'start', 'interval', 'noise', 'number', 'weight', 'delay']]
        netParams.stimSourceParams[key] = {'type': 'NetStim', 'start': start, 'interval': interval, 'noise': noise, 'number': number}

        if not isinstance(pop, list):
            pop = [pop]

        for eachPop in pop:
            # connect stim source to target

            netParams.stimTargetParams[key + '_' + eachPop] = {
                'source': key,
                'conds': {'pop': eachPop, 'ynorm': ynorm},
                'sec': sec,
                'loc': loc,
                'synMech': synMech,
                'weight': weight,
                'synMechWeightFactor': synMechWeightFactor,
                'delay': delay}

# ------------------------------------------------------------------------------
# Description
# ------------------------------------------------------------------------------

netParams.description = """
v7 - Added template for connectivity
v8 - Added cell types
v9 - Added local connectivity
v10 - Added thalamic populations from prev model
v11 - Added thalamic conn from prev model
v12 - Added CT cells to L5B
v13 - Added CT cells to L5A
v14 - Fixed L5A & L5B E cell densities + added CT5A & CT5B to 'Epops'
v15 - Added cortical and thalamic conn to CT5A and CT5B 
v16 - Updated multiple cell types
v17 - Changed NGF -> I prob from strong (1.0) to weak (0.35)
v18 - Fixed bug in VIP cell morphology
v19 - Added in 2-compartment thalamic interneuron model 
v20 - Added TI conn and updated thal pop
v21 - Added exc+inh bkg inputs specific to each cell type
v22 - Made exc+inh bkg inputs specific to each pop; automated calculation
v23 - IE/II specific layer gains and simplified code (assume 'Allen_custom')
v24 - Fixed bug in IE/II specific layer gains
v25 - Fixed subconnparams TC->E and NGF1->E; made IC input deterministic
v26 - Changed NGF AMPA:NMDA ratio 
v27 - Split thalamic interneurons into core and matrix (TI and TIM)
v28 - Set recurrent TC->TC conn to 0
v29 - Added EI specific layer gains
v30 - Added EE specific layer gains; and split combined L1-3 gains into L1,L2,L3
v31 - Added EI postsyn-cell-type specific gains; update ITS4 and NGF
v32 - Added IE presyn-cell-type specific gains
v33 - Fixed bug in matrix thalamocortical conn (were very low)
v34 - Added missing conn from cortex to matrix thalamus IREM and TIM
v35 - Parametrize L5B PT Ih and exc cell K+ conductance (to simulate NA/ACh modulation) 
v36 - Looped speech stimulus capability added for cfg.ICThalInput
v37 - Adding in code to modulate t-type calcium conductances in thalamic and cortical cells
v38 - Adding in code to modulate NMDA synaptic weight from E --> I populations 
v39 - Changed E --> I cfg.NMDARfactor such that weight is not a list, but instead a single value 
v40 - added parameterizations from Christoph Metzner for localizing the large L1 sink
v41 - modifying cochlea to Thal -> A1 for tonotopic gradient, adding functions
v42 - Changed inhibitory receptor ratios for GABAB and NGF as well as altering the cochlear -> thalamic connections (prob and wieght)
v43 - Updated intrathalamic IE and EI parameters to create a more gradual reduction in TC cell mV over the course of stims 
v44 - Increased EEGain and decreased IEGain to increase the evoked activity in cortical pops
v45 - Updated background -> Ctx E and Ctx I pops and Bkg - > Thalamic E pops
"""
