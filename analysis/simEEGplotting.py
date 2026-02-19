from IPython.core.pylabtools import figsize
from netpyne import sim
from netpyne.plotting import plotCSDPSD
from netpyne.support.morlet import MorletSpec, index2ms
from netpyne.analysis import spikes_legacy
from simTools import simPlotting
import os
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt
from lfpykit.eegmegcalc import NYHeadModel

stim_on = 3000  # Define onset of stimulus if necessary
calcEEG = {'start': stim_on, 'stop': 4000}
# calcMEG = {'start': stim_on, 'stop': 4000}
filter = {'lowCut': 5, 'hiCut': 1000}
plotERP = {'useFilter': True}
# plotSpectrogram = {'useFilter': True}
# plotPSD = {'useFilter': False}
# plotRaster = {'timeRange': [2500, 5000]}
# PSDSpect = {'timeRange': [3000, 5000], 'useLFP': False, 'useCSD': True}
# plotMUA = {'stimDur': 1000}

# calcEEG = False
calcMEG = False
# filter = False
# plotERP = False
plotSpectrogram = False
plotPSD = False
plotRaster = False
PSDSpect = False
plotMUA = False


batch = 'Scz_grid_0312'  # Name of batch for fig saving

# Load sim EEG data
base_dir = '/Users/scoot/A1ProjData/A1_sim_data/' + batch + '/'  # Define dir from saved data dir
# base_dir = '../simOutput/' + batch + '/'
figure_dir = '/Users/scoot/A1ProjData/A1_figs/SIMfigs/'  # Define dir for saving figures

nmda_per_file = {}
# Loop through all files in the directory
for file in os.listdir(base_dir):
    if file.endswith('_data.pkl') or file.endswith('_data.json'): # make sure you only download output data

        sim.initialize()
        # all = sim.loadSimData('/Users/scoot/A1ProjData/A1_sim_data/EIvsIETune0930_00002_data.pkl')
        all = sim.loadAll(os.path.join(base_dir, file), instantiate=False)# Valery did this and fixed some problems, not sure why necessary
        fname = file[0:-9] # Create filename (can change to whatever)
        if not os.path.exists(figure_dir + batch):
            os.mkdir(figure_dir + batch)  # Create Figure directory if one doesn't already exist

        save_dir = str(figure_dir + batch + '/' + fname)  # Define save directory for figures

        if calcEEG:
            stim_eeg, stim_window = simPlotting.calculateEEG(
                    sim   = sim,
                    start = calcEEG['start'],
                    end   = calcEEG['stop']
                )  # Calculate EEG signal at one electode (currently set to 'Cz')

            offsetStart = calcEEG['start'] - stim_on
            endWindow = calcEEG['stop'] - stim_on
            t = np.arange(offsetStart, endWindow, 0.05) # Time vector starting at t=0 instead of timeRange[0]

        if calcMEG:
            stim_meg, stim_window = simPlotting.calculateMEG(
                    sim   = sim,
                    start = calcMEG['start'],
                    end   = calcMEG['stop']
                )

            offsetStart = calcMEG['start'] - stim_on
            endWindow = calcMEG['stop'] - stim_on
            t = np.arange(offsetStart, endWindow, 0.05) # Time vector starting at t=0 instead of timeRange[0]

        # Filter EEG data
        if filter:
            if calcEEG:
                filtered_eeg = simPlotting.filterEEG(
                        signal     = stim_eeg,
                        lowcut  = filter['lowCut'],
                        highcut = filter['hiCut'],
                        fs      = 20000,
                        order   = 2
                    )
            if calcMEG:
                filtered_meg = simPlotting.filterEEG(
                        signal    = stim_meg,
                        lowcut  = filter['lowCut'],
                        highcut = filter['hiCut'],
                        fs      = 20000,
                        order   = 2
                    )

        # Plot ERP
        t_sec = [(tim/1000) + 4 for tim in t]
        if plotERP:
            if filter:
                if calcEEG:
                    simPlotting.plotERP(
                        data     = filtered_eeg,
                        time     = t_sec,
                        save_dir=save_dir + '_EEG_',
                        units='uV'
                    )  # Create filtered ERP plot of time window specified

                if calcMEG:
                    simPlotting.plotERP(
                        data     = filtered_meg,
                        time     = t_sec,
                        save_dir=save_dir + '_MEG_',
                        units='T'
                    )  # Create filtered ERP plot of time window specified

            else:
                if calcEEG:
                    simPlotting.plotERP(
                        data     = stim_eeg,
                        time     = t,
                        save_dir = save_dir + '_EEG_',
                        units = 'uV'
                    )  # Create unfiltered ERP plot of time window specified
                if calcMEG:
                    simPlotting.plotERP(
                        data     = stim_meg,
                        time     = t,
                        save_dir = save_dir + '_MEG_',
                        units = 'T'
                    )  # Create unfiltered ERP plot of time window specified

        # Plot EEG Spectrogram
        if plotSpectrogram:
            if plotSpectrogram['useFilter'] == True:
                if calcEEG:
                    simPlotting.plot_spectrogram(
                        data     = filtered_eeg,
                        time     = t,
                        save_dir = save_dir + '_EEG_',
                        type = 'EEG'
                    )
                if calcMEG:
                    simPlotting.plot_spectrogram(
                        data=filtered_eeg,
                        time=t,
                        save_dir=save_dir + '_MEG_',
                        type = 'MEG'
                    )

            # else:
            #     simPlotting.plot_spectrogram(
            #         data     = stim_eeg,
            #         time     = t,
            #         save_dir = save_dir + '_MEG_'
            #     )

        # Plot EEG PSD
        if plotPSD:
            if plotPSD['useFilter'] == True:
                simPlotting.plot_PSD(
                    data     = filtered_eeg,
                    save_dir = save_dir
                )

            else:
                simPlotting.plot_PSD(
                    data     = stim_eeg,
                    save_dir = save_dir,
                    time = t
                )

        # Plot Raster
        if plotRaster:
                sim.analysis.plotRaster(
                    include      = [sim.cfg.allpops],      #plotRaster['include'],
                    orderInverse = True,
                    timeRange    = plotRaster['timeRange'],
                    markerSize   = 50,
                    figSize      = (25, 25),
                    saveFig      = str(save_dir + '_raster.png')
                )


        if PSDSpect:
            simPlotting.plotPSDSpectrogram(
                    sim       = sim,
                    save_dir  = save_dir,
                    timeRange = PSDSpect['timeRange'],
                    useLFP    = PSDSpect['useLFP'],
                    useCSD    = PSDSpect['useCSD']
                )


        if plotMUA:
            starts = []
            pops = ['ITS4'] #['IT2', 'PV2', 'SOM2', 'VIP2', 'NGF2', 'IT3',
            #         'ITP4', 'ITS4', 'IT5A', 'CT5A', 'IT5B', 'PT5B',
            #         'CT5B', 'IT6', 'CT6', 'TC', 'HTC', 'IRE', 'TI']
            for i in range(sim.cfg.numInjections):
                starts.append(i * sim.cfg.injectionInterval)
            for pop in pops:
                simPlotting.plotMUApops(
                        sim             = sim,
                        populations     = [pop],
                        bin_start_times = starts,
                        bin_duration    = plotMUA['stimDur'],
                        save_dir        = save_dir + '_' + pop
                    )


################## Scrap for resampling if needed later ##################################################
# num_samples = len(stim_data)
# new_num_samples = int(num_samples * 1000/ 20000)
# resampled_data = signal.resample(stim_data, new_num_samples)
