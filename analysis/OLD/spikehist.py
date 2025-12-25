import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import pickle
import collections
from netpyne import sim, specs

# Spike Hist
from netpyne.analysis.spikes_legacy import plotSpikeHist


# Global population params
allpops = ['NGF1', 'IT2', 'SOM2', 'PV2', 'VIP2', 'NGF2', 'IT3',  'SOM3', 'PV3', 'VIP3', 'NGF3', 'ITP4', 'ITS4', 'SOM4', 'PV4', 'VIP4', 'NGF4', 'IT5A', 'CT5A', 'SOM5A', 'PV5A', 'VIP5A', 'NGF5A', 'IT5B', 'PT5B', 'CT5B',  'SOM5B', 'PV5B', 'VIP5B', 'NGF5B', 'IT6', 'CT6', 'SOM6', 'PV6', 'VIP6', 'NGF6', 'TC', 'TCM', 'HTC', 'IRE', 'IREM', 'TI', 'TIM', 'IC']
excpops = ['IT2', 'IT3', 'ITP4', 'ITS4', 'IT5A', 'CT5A', 'IT5B', 'PT5B', 'CT5B', 'IT6', 'CT6', 'TC', 'TCM', 'HTC', 'IC']
inhpops = ['NGF1', 'SOM2', 'PV2', 'VIP2', 'NGF2', 'SOM3', 'PV3', 'VIP3', 'NGF3', 'SOM4', 'PV4', 'VIP4', 'NGF4', 'SOM5A', 'PV5A', 'VIP5A', 'NGF5A', 'SOM5B', 'PV5B', 'VIP5B', 'NGF5B', 'SOM6', 'PV6', 'VIP6', 'NGF6', 'IRE', 'IREM', 'TI', 'TIM']
supra =  ['NGF1', 'IT2', 'SOM2', 'PV2', 'VIP2', 'NGF2', 'IT3',  'SOM3', 'PV3', 'VIP3', 'NGF3']
gran = ['ITP4', 'ITS4', 'SOM4', 'PV4', 'VIP4', 'NGF4']
infra = ['IT5A', 'CT5A', 'SOM5A', 'PV5A', 'VIP5A', 'NGF5A', 'IT5B', 'PT5B', 'CT5B',  'SOM5B', 'PV5B', 'VIP5B', 'NGF5B', 'IT6', 'CT6']
supraE =  ['IT2', 'IT3']
granE = ['ITP4', 'ITS4']
infraE = ['IT5A', 'CT5A', 'IT5B', 'PT5B', 'CT5B', 'IT6', 'CT6']
supraI =  ['NGF1', 'SOM2', 'PV2', 'VIP2', 'NGF2', 'SOM3', 'PV3', 'VIP3', 'NGF3']
granI = ['SOM4', 'PV4', 'VIP4', 'NGF4']
infraI = ['SOM5A', 'PV5A', 'VIP5A', 'NGF5A', 'SOM5B', 'PV5B', 'VIP5B', 'NGF5B', 'SOM6', 'PV6', 'VIP6', 'NGF6']
thal = ['TC', 'TCM', 'HTC']
cortexE = ['IT2', 'IT3', 'ITP4', 'ITS4', 'IT5A', 'CT5A', 'IT5B', 'PT5B', 'CT5B', 'IT6', 'CT6']
cortexAll = ['NGF1', 'IT2', 'SOM2', 'PV2', 'VIP2', 'NGF2', 'IT3',  'SOM3', 'PV3', 'VIP3', 'NGF3', 'ITP4', 'ITS4', 'SOM4', 'PV4', 'VIP4', 'NGF4', 'IT5A', 'CT5A', 'SOM5A', 'PV5A', 'VIP5A', 'NGF5A', 'IT5B', 'PT5B', 'CT5B',  'SOM5B', 'PV5B', 'VIP5B', 'NGF5B', 'IT6', 'CT6', 'SOM6', 'PV6', 'VIP6', 'NGF6']
l4 = ['ITP4', 'ITS4']
includeList = ['IC', thal, l4]
includeLabels = ['IC_thal_cxE']

timeRange = [4000, 5000]  # for plot
lineWidth = 10.0
# popColors = {'IC':'b', 'TCM':'y', 'HTC':'y','TC':'y', 'ITP4':'saddlebrown', 'ITS4':'saddlebrown'}
sim.load('/Users/scottmcelroy/A1_scz/A1_sim_data/ASSR_tune_0228_data.pkl', 'rb',
         instantiateStims=False, instantiateConns=False)

fig_hist, data_hist = plotSpikeHist(include=includeList,linewidth=lineWidth,figSize=(100, 25),showFig=True, legendLabels=['IC', 'Thalamus', 'Cx Layer 4'], timeRange=timeRange, saveFig='/Users/scottmcelroy/A1_scz/A1_figs/spikehist.png')
plt.rcParams.update({'font.size': 30})
plt.tick_params(axis='both', which='major', labelsize=20)


