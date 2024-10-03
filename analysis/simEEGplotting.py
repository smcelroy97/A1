from netpyne import sim
from netpyne.plotting import plotCSDPSD
from netpyne.support.morlet import MorletSpec, index2ms
from netpyne.analysis import spikes_legacy
from simTools import simTools
import os
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt
from lfpykit.eegmegcalc import NYHeadModel

stim_on = 2000  # Define onset of stimulus if necessary
# calcEEG = {'start': 1000, 'stop': 6000}
# filter = {'lowCut':2, 'hiCut': 12}
# plotERP = {'useFilter': True}
# plotSpectrogram = {'useFilter': False}
# plotPSD = {'useFilter': True}
# plotRaster = {'timeRange': [1000, 6500]}
# PSDSpect = {'timeRange': [3000, 4000], 'useLFP': False, 'useCSD': True}
plotMUA = {'populations': ['TC', 'HTC'], 'stimDur': 100}

calcEEG = False
filter = False
plotERP = False
plotSpectrogram = False
plotPSD = False
plotRaster = False
PSDSpect = False
# plotMUA = False


batch = 'GABAB_KO1003'  # Name of batch for fig saving

# Load sim EEG data
base_dir = '/Users/scoot/A1ProjData/A1_sim_data/' + batch + '/'  # Define dir from saved data dir
figure_dir = '/Users/scoot/A1ProjData/A1_figs/SIMfigs/' # Define dir for saving figures

# Loop through all files in the directory
for file in os.listdir(base_dir):
    if file.endswith('_data.pkl') or file.endswith('_data.json'): # make sure you only download output data
        sim.initialize()
        all = sim.loadAll(os.path.join(base_dir, file))  # Valery did this and fixed some problems, not sure why necessary
        fname = file[0:-9] # Create filename (can change to whatever)
        if not os.path.exists(figure_dir + batch):
            os.mkdir(figure_dir + batch)  # Create Figure directory if one doesn't already exist

        save_dir = str(figure_dir + batch + '/' + fname)  # Define save directory for figures


        if calcEEG:
            stim_data, stim_window = simTools.calculateEEG(
                    sim   = sim,
                    start = calcEEG['start'],
                    end   = calcEEG['stop']
                )  # Calculate EEG signal at one electode (currently set to 'Cz')

            offsetStart = calcEEG['start'] - stim_on
            endWindow = calcEEG['stop'] - stim_on
            t = np.arange(offsetStart, endWindow, 0.05) # Time vector starting at t=0 instead of timeRange[0]

        # Filter EEG data
        if filter:
            filtered_data = simTools.filterEEG(
                    EEG     = stim_data,
                    lowcut  = filter['lowCut'],
                    highcut = filter['hiCut'],
                    fs      = 20000,
                    order   = 2
                )

        # Plot ERP '
        if plotERP:
            if plotERP['useFilter'] == True:
                simTools.plotERP(
                    data     = filtered_data,
                    time     = stim_window,
                    save_dir = save_dir
                )  # Create filtered ERP plot of time window specified

            else:
                simTools.plotERP(
                    data     = stim_data,
                    time     = t,
                    save_dir = save_dir
                )  # Create unfiltered ERP plot of time window specified

        # Plot EEG Spectrogram
        if plotSpectrogram:
            if plotSpectrogram['useFilter'] == True:
                simTools.plot_spectrogram(
                    data     = filtered_data,
                    time     = t,
                    save_dir = save_dir
                )

            else:
                simTools.plot_spectrogram(
                    data     = stim_data,
                    time     = t,
                    save_dir = save_dir
                )

        # Plot EEG PSD
        if plotPSD:
            if plotPSD['useFilter'] == True:
                simTools.plot_PSD(
                    data     = filtered_data,
                    save_dir = save_dir
                )

            else:
                simTools.plot_PSD(
                    data     = stim_data,
                    save_dir = save_dir
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
            simTools.plotPSDSpectrogram(
                    sim       = sim,
                    save_dir  = save_dir,
                    timeRange = PSDSpect['timeRange'],
                    useLFP    = PSDSpect['useLFP'],
                    useCSD    = PSDSpect['useCSD']
                )


        if plotMUA:
            simTools.plotMUApops(
                    sim             = sim,
                    populations     = plotMUA['populations'],
                    bin_start_times = [2000, 2724, 3448, 4172, 4896, 5620, 6344],
                    bin_duration    = plotMUA['stimDur'],
                    save_dir        = save_dir
                )

            # plotPops = ['TC']
            # try:
            #   record_pops = [(pop, list(np.arange(0, netParams.popParams[pop]['numCells']))) for pop in plotPops]
            # except:
            #   record_pops = [(pop, list(np.arange(0, 40))) for pop in plotPops]
            #
            # for pop_ind, pop in enumerate(plotPops):
            #   print('\n\n', pop)
            #   # sim.analysis.plotTraces(
            #   figs, traces_dict = sim.analysis.plotTraces(
            #     include=[pop],
            #     # include=[record_pops[pop_ind]],
            #     # timeRange=[490,550],
            #     overlay=True, oneFigPer='trace',
            #     ylim=[-110, 50],
            #     axis=True,
            #     figSize=(70, 15),
            #     # figSize=(40, 15),
            #     # figSize=(60, 18),
            #     fontSize=15,
            #     # saveFig=True,
            #     # saveFig=sim.cfg.saveFigPath+'/'+sim.cfg.filename+'_traces_'+pop+ '.png',
            #     saveFig=sim.cfg.saveFolder + '/' + sim.cfg.simLabel + '_traces__' + pop + '.png',
            #   )
            #
            #   tracesData = traces_dict['tracesData']
            #   # store_v={}
            #   store_v = []
            #   store_voltages = {}
            #   for rec_ind in range(len(tracesData)):
            #     for trace in tracesData[rec_ind].keys():
            #       if '_V_soma' in trace:
            #         cell_gid_str = trace.split('_V_soma')[0].split('cell_')[1]
            #         # store_v.update({cell_gid_str:list(tracesData[rec_ind][trace])})
            #         store_v.append(list(tracesData[rec_ind][trace]))
            #         store_voltages.update({cell_gid_str: list(tracesData[rec_ind][trace])})
            #
            #   t_vector = list(tracesData[0]['t'])
            #   mean_v = np.mean(store_v, axis=0)
            #   t_vector_ = [t_vector[i] for i in range(len(mean_v))]
            #   plt.figure(figsize=(70, 15))
            #   for trace in store_v: plt.plot(t_vector_, trace, 'gray', alpha=0.2)
            #   plt.plot(t_vector_, mean_v, 'r')
            #   plt.ylim([-110, 50])
            #   plt.xlim([min(t_vector_), max(t_vector_)])
            #   # plt.plot(mean_v,'k')
            #   plt.savefig(save_dir + '_mean_traces_' + pop + '.png')

            # sim.analysis.plotTraces(include = [('TC', i) for i in range(1)], saveFig = save_dir)
            # sim.plotting.plotCSD(overlay = 'LFP', timeRange =[3000, 3600], saveFig='/Users/scottmcelroy/A1_scz/A1_figs/SIMfigs/'
            #                 + batch + '/' + fname + '_CSD.png')
# # Plot LFP PSD
#         sim.analysis.plotLFP(plots = 'PSD', saveFig= '/Users/scottmcelroy/A1_scz/A1_figs/SIMfigs/'+batch+ '/'+fname+ 'LFP.png')
# # Plot CSD
#         sim.plotting.plotCSD(overlay= 'CSD', timeRange=[2500, 5000],saveFig='/Users/scottmcelroy/A1_scz/A1_figs/SIMfigs/' + batch+'/'+fname+'CSDpad.jpeg')
#         spikes_legacy.plotRatePSD(include = ['IT2', 'IT3', 'ITP4', 'ITS4', 'IT5A', 'CT5A', 'IT5B', 'CT5B' , 'PT5B', 'IT6', 'CT6'],timeRange=[3000, 5000],  saveFig='/Users/scottmcelroy/Desktop/ASSRratePSDAll.png')
#         spikes_legacy.plotSpikeHist(include = ['cochlea', 'TC'], timeRange=[3000, 6000], saveFig='/Users/scottmcelroy/A1_scz/A1_figs/SIMfigs/' + batch + '/' + fname + 'RateHisto')
        # spikes_legacy.plotSpikeStats(saveFig= '/Users/scottmcelroy/A1_scz/A1_figs/SIMfigs/' + batch + '/' + fname + 'SpikeStats')
# spikes_legacy.plotRatePSD(include = ['IT5A', 'CT5A'], timeRange=[3000, 5000], saveFig='/Users/scottmcelroy/Desktop/ASSRratePSDL5A.png')
# spikes_legacy.plotRatePSD(include = ['IT5B', 'CT5B' , 'PT5B'], timeRange=[3000, 5000], saveFig='/Users/scottmcelroy/Desktop/ASSRratePSDL5B.png')
# spikes_legacy.plotRatePSD(include = ['IT6', 'CT6'], timeRange=[3000, 5000], saveFig='/Users/scottmcelroy/Desktop/ASSRratePSDL6.png')


################## Scrap for resampling if needed later ##################################################
# num_samples = len(stim_data)
# new_num_samples = int(num_samples * 1000/ 20000)
# resampled_data = signal.resample(stim_data, new_num_samples)