from lfpykit.eegmegcalc import NYHeadModel
from scipy import signal
from scipy.signal import butter, filtfilt
from netpyne.support.morlet import MorletSpec, index2ms
import os
import numpy as np
import matplotlib
import random
from    matplotlib  import  pyplot  as plt

#########################################################################
#    Funcitons for analysis, code to use found in simEEGplotting.py     #
#########################################################################
class simPlotting:
    def calculateEEG(
            sim,
            start,
            end
    ):

        # Load 3D head model for EEG
        nyhead = NYHeadModel(nyhead_file=os.getenv('NP_LFPYKIT_HEAD_FILE', None))
        nyhead.set_dipole_pos([ 39.74573803, -21.57684261, 7.82510972])
        M = nyhead.get_transformation_matrix()

        # Adjsut time for stimulation window
        timeRange = [start, end]
        timeSteps = [int(timeRange[0] / 0.05), int(timeRange[1] / 0.05)]
        t = np.arange(timeRange[0], timeRange[1], 0.05)

        # gather dipole data
        p = sim.allSimData['dipoleSum']
        p = np.array(p).T
        p = p[:, timeSteps[0]: timeSteps[1]]
        p = nyhead.rotate_dipole_to_surface_normal(p)

        # Calculate EEG
        eeg = M @ p * 1e9
        goodchan = eeg[48, :]
        # goodchan = eeg[38]

        onset = int(start / 0.05)
        offset = int(end / 0.05)
        return goodchan, t

    def filterEEG(
            EEG,
            lowcut,
            highcut,
            fs,
            order
    ):

        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        filtered_signal = filtfilt(b, a, EEG)
        return filtered_signal

    def plotERP(
            data,
            time,
            save_dir,
            figsize = (30,20)
    ):

        plt.figure(figsize=figsize)
        plt.plot(time,data/1000, color='black', linewidth = 8)
        plt.axhline(y=0, color='black',linestyle='-', linewidth = 4)
        plt.tick_params(labelsize=50)
        plt.xlabel('Time (ms)', fontsize = 65)
        plt.ylabel('uV', fontsize = 65)
        plt.savefig(save_dir + '_ERP.png')
        print('saved')

    def plot_spectrogram(
            data,
            time,
            save_dir,
            figsize = (20,20)
    ):

        # sampling frequency
        fs = int(1000.0 / 0.05)

        # Define freqs you care about
        minFreq = 1
        maxFreq = 80

        # Perform Morlet transform
        freqList = None
        spec = (MorletSpec(
            data,
            fs,
            freqmin  = minFreq,
            freqmax  = maxFreq,
            freqstep = 1,
            lfreq    = freqList))

        # Min and mox for the color of normalized power
        vmin = spec.TFR.min()
        vmax = spec.TFR.max()

        T = time  # Time
        F = spec.f  # Define frequencies
        S = spec.TFR  # Spectral data for spectrogram

        # Spectrogram plot params
        plt.figure(figsize=figsize)
        plt.tick_params(labelsize=50)
        plt.xlabel('Time (ms)', fontsize = 65)
        plt.ylabel('Frequency (Hz)', fontsize = 65)
        plt.imshow(
            S,
            extent        = (np.amin(T), np.amax(T), np.amin(F), np.amax(F)),
            origin        = 'lower',
            interpolation = 'None',
            aspect        = 'auto',
            vmin          = vmin,
            vmax          = vmax,
            cmap          = plt.get_cmap('viridis')
            )
        plt.savefig(save_dir + '_EEGspect.png')


    def plot_PSD(
            data,
            save_dir,
            figsize = (20,20)
    ):
        # sampling frequency
        fs = int(1000.0 / 0.05)

        # Define freqs you care about
        minFreq = 1
        maxFreq = 60

        # Perform Morlet transform
        freqList = None
        spec = (MorletSpec(
            data,
            fs,
            freqmin  = minFreq,
            freqmax  = maxFreq,
            freqstep = 1,
            lfreq    = freqList))

        # Min and mox for the color of normalized power
        vmin = spec.TFR.min()
        vmax = spec.TFR.max()

        T = time  # Time
        F = spec.f  # Define frequencies
        S = spec.TFR  # Spectral data for spectrogram
        signal = 10 * (np.log10(np.mean(S, 1)))  # Use this for PSD plotting

        # PSD plot params
        plt.figure(figsize=figsize)
        plt.xlabel('Frequency')
        plt.ylabel('Power')
        plt.plot(F, signal)
        plt.savefig(save_dir + '_PSD.png')


    def plotPSDSpectrogram(
            sim,
            save_dir,
            timeRange,
            showMin  = 1,
            showMax  = 100,
            filtFreq = False,
            useLFP   = True,
            useCSD   = True
    ):

        if useCSD and useLFP:
            lfp_PSD = sim.analysis.preparePSD(
                CSD       = False,
                minFreq   = showMin,
                maxFreq   = showMax,
                filtFreq  = filtFreq,
                timeRange = timeRange
            )

            csd_PSD = sim.analysis.preparePSD(
                CSD       = True,
                minFreq   = showMin,
                maxFreq   = showMax,
                filtFreq  = filtFreq,
                timeRange = timeRange
            )

            plt.figure(figsize=(12, 6))
            plt.subplot(121)
            plt.imshow(lfp_PSD['psdSignal'], aspect='auto', origin='lower', cmap='viridis')
            plt.gca().invert_yaxis()
            plt.colorbar(label='LFP Amplitude')
            plt.xlim([20, 100])
            plt.xlabel('Frequency')
            plt.ylabel('Electrode Depth')
            plt.title('Local Field Potential (LFP) PSD Spectrogram')

            # Plotting the CSD heatmap
            plt.subplot(122)
            plt.imshow(csd_PSD['psdSignal'], aspect='auto', origin='lower', cmap='viridis')
            plt.gca().invert_yaxis()
            plt.colorbar(label='CSD Amplitude')
            plt.xlim([20, 100])
            plt.xlabel('Frequency')
            plt.ylabel('Electrode Depth')
            plt.title('Current Source Density (CSD) PSD Spectrogram')

            plt.tight_layout()
            plt.savefig(save_dir + '_CSDPSDspect.png')

        elif useLFP and not useCSD:
            lfp_PSD = sim.analysis.preparePSD(
                CSD       = False,
                minFreq   = showMin,
                maxFreq   = showMax,
                filtFreq  = filtFreq,
                timeRange = timeRange
            )

            plt.figure()
            plt.imshow(lfp_PSD['psdSignal'], aspect='auto', origin='lower', cmap='viridis')
            plt.gca().invert_yaxis()
            plt.colorbar(label='LFP Amplitude')
            plt.xlim([20, 100])
            plt.xlabel('Frequency')
            plt.ylabel('Electrode Depth')
            plt.title('Local Field Potential (LFP) PSD Spectrogram')
            plt.savefig(save_dir + '_LFPPSDspect.png')

        else:
            csd_PSD = sim.analysis.preparePSD(
                CSD       = True,
                minFreq   = showMin,
                maxFreq   = showMax,
                filtFreq  = filtFreq,
                timeRange = timeRange
            )

            plt.figure()
            plt.imshow(csd_PSD['psdSignal'], aspect='auto', origin='lower', cmap='viridis')
            plt.gca().invert_yaxis()
            plt.colorbar(label='CSD Amplitude')
            plt.xlim([20, 100])
            plt.xlabel('Frequency')
            plt.ylabel('Electrode Depth')
            plt.title('Current Source Density (CSD) PSD Spectrogram')

            plt.tight_layout()
            plt.savefig(save_dir + '_CSDPSDspect.png')

    def plotMUApops(
            sim,
            bin_start_times,
            bin_duration,
            populations,
            save_dir
    ):
        # Initialize an empty dictionary to store the firing rates for each population
        firing_rates = {}

        # Calculate the bin end times
        bin_end_times = [start + bin_duration for start in bin_start_times]

        # Loop over each population
        for pop in populations:
            # Get the spike times for the current population
            pop_spike_times = np.array([t for i, t in zip(sim.allSimData['spkid'], sim.allSimData['spkt']) if
                                        i in sim.net.allPops[pop]['cellGids']])

            # Initialize an empty list to store the firing rates for the current population
            pop_firing_rates = []

            # Loop over each bin
            for start, end in zip(bin_start_times, bin_end_times):
                # Count the number of spikes in the current bin
                count = np.sum((pop_spike_times >= start) & (pop_spike_times < end))

                # Calculate the firing rate and append it to the list
                rate = count / (bin_duration / 1000)  # Convert to Hz
                pop_firing_rates.append(rate)

            # Store the firing rates for the current population
            firing_rates[pop] = pop_firing_rates
        # Plot the firing rates
        plt.rcParams['font.weight'] = 'bold'
        # plt.figure(figsize = (27.5, 12.5))
        plt.figure(figsize=(15.5, 12.5))
        current = np.linspace(0, 0.6, 13)
        for pop, rates in firing_rates.items():
            plt.plot(current, rates, label=pop, linewidth = 6)
        # plt.xlabel('Stimulus Index', fontsize = 30, fontweight = 'bold')
        plt.xlabel('Current (pA)', fontsize=30, fontweight='bold')
        plt.ylabel('Firing Rate (Hz)', fontsize = 30, fontweight = 'bold')
        # plt.xticks(range(0, (len(bin_start_times))), fontsize = 25)
        plt.xticks(fontsize=25)
        plt.ylim(0,150)
        plt.yticks(fontsize = 25)
        # plt.title('MUA w/ GABA B', fontsize=50, fontweight = 'bold')  # Add title to the plot
        plt.title(populations[0], fontsize=50, fontweight='bold')
        plt.legend(fontsize = 30)
        plt.savefig(save_dir + '_MUA.png')

    def plotMeanTraces(sim, cellsPerPop, plotPops):
        record_pops = [(pop, list(np.arange(0, cellsPerPop))) for pop in plotPops]
        for pop_ind, pop in enumerate(plotPops):
            print('\n\n', pop)
            figs, traces_dict = sim.analysis.plotTraces(
                include=[record_pops[pop_ind]],
                axis=True,
                figSize=(18, 15),
                fontSize=15,
                saveFig=False
            )
            tracesData = traces_dict['tracesData']
            store_v = []
            store_voltages = {}
            for rec_ind in range(len(tracesData)):
                for trace in tracesData[rec_ind].keys():
                    if '_V_soma' in trace:
                        cell_gid_str = trace.split('_V_soma')[0].split('cell_')[1]
                        store_v.append(list(tracesData[rec_ind][trace]))
                        store_voltages.update({cell_gid_str: list(tracesData[rec_ind][trace])})

            t_vector = list(tracesData[0]['t'])
            mean_v = np.mean(store_v, axis=0)
            t_vector_ = [t_vector[i] for i in range(len(mean_v))]
            plt.figure(figsize=(20, 15))
            for trace in store_v: plt.plot(t_vector_, trace, 'gray', alpha=0.2)
            plt.title(pop)
            plt.plot(t_vector_, mean_v, 'r')
            plt.ylim([-110, 50])
            plt.xlim([min(t_vector_), max(t_vector_)])
            plt.savefig(sim.cfg.saveFolder + '/' + sim.cfg.simLabel + '_mean_traces_' + pop + '.png')

    def plotOUheatMap(
            df_path,                    # Data of interest
            save_dir,                   # Path to save figs
            pops = None,                # Pops you wish to plot
            stats = ['rate', 'isicv']   # Rate, isicv or both
    ):
        import os
        import pickle
        import seaborn as sns
        import pandas as pd
        from matplotlib import ticker

        if os.path.exists(df_path):
            with open(df_path, 'rb') as file:
                df = pickle.load(file)

        if pops == None:
            pops = [pop for pop in df['rate']]

        for stat in stats:
            if stat == 'rate':
                for pop in pops:
                    df['rate'][pop] = df['rate'][pop].apply(pd.to_numeric, errors='coerce')

                    # Plot the DataFrame as a heatmap
                    plt.figure(figsize=(10, 8))
                    ax = sns.heatmap(df['rate'][pop], annot=False, fmt=".2f", cmap="viridis")
                    plt.title(f'Heatmap of Rate DataFrame for Population {pop}')
                    plt.xlabel('OUamp')
                    plt.ylabel('OUstd')
                    ax.invert_yaxis()

                    # Set the tick labels to the actual values
                    ax.set_xticks(range(len(df['rate'][pop].columns)))
                    ax.set_xticklabels(df['rate'][pop].columns, rotation=45, ha='right')
                    ax.set_yticks(range(len(df['rate'][pop].index)))
                    ax.set_yticklabels(df['rate'][pop].index, rotation=0)

                    # Add color bar with units
                    cbar = ax.collections[0].colorbar
                    cbar.set_label('Rate (Hz)', rotation=270, labelpad=15)

                    plt.savefig(save_dir + pop + '_rate_Heatmap')

            if stat == 'isicv':
                for pop in pops:
                    df['isicv'][pop] = df['isicv'][pop].apply(pd.to_numeric, errors='coerce')

                    # Plot the DataFrame as a heatmap
                    plt.figure(figsize=(10, 8))
                    ax = sns.heatmap(df['isicv'][pop], annot=False, fmt=".2f", cmap="viridis")
                    plt.title(f'Heatmap of ISICV DataFrame for Population {pop}')
                    plt.xlabel('OUamp')
                    plt.ylabel('OUstd')
                    ax.invert_yaxis()

                    # Set the tick labels to the actual values
                    ax.set_xticks(range(len(df['isicv'][pop].columns)))
                    ax.set_xticklabels(df['isicv'][pop].columns, rotation=45, ha='right')
                    ax.set_yticks(range(len(df['isicv'][pop].index)))
                    ax.set_yticklabels(df['isicv'][pop].index, rotation=0)

                    # Add color bar with units
                    cbar = ax.collections[0].colorbar
                    cbar.set_label('ISICV', rotation=270, labelpad=15)

                    plt.savefig(save_dir + pop + '_isicv_Heatmap')


#########################################################################
#    Funcitons for editing a network after cells and conns are made     #
#########################################################################
class editNet:

    def pruneSynapsesVol(
            cell,
            conn,
            probability,
            pruning_range
    ):
        # Get the section
        sec = cell.secs[conn['sec']]

        # Get the 3D points of the section
        points = sec['geom']['pt3d']

        y1 = points[0][1]
        y2 = points[1][1]

        syn_rel = conn['loc'] * (y2 - y1)

        # Get the position of the cell within the network
        y_cell = cell.tags['y']

        # Calculate the 3D coordinates relative to the network
        y_net = syn_rel + y_cell
        if pruning_range[1] > y_net > pruning_range[0]:
            if random.random() < probability:
                cell.conns.remove(conn)

    def setdminID(sim, lpop):
        # setup min,max ID and dnumc for each population in lpop
        alltags = sim._gatherAllCellTags()  # gather cell tags; see https://github.com/Neurosim-lab/netpyne/blob/development/netpyne/sim/gather.py
        dGIDs = {pop: [] for pop in lpop}
        for tinds in range(len(alltags)):
            if alltags[tinds]['pop'] in lpop:
                dGIDs[alltags[tinds]['pop']].append(tinds)
        sim.simData['dminID'] = {pop: np.amin(dGIDs[pop]) for pop in lpop if len(dGIDs[pop]) > 0}
        sim.simData['dmaxID'] = {pop: np.amax(dGIDs[pop]) for pop in lpop if len(dGIDs[pop]) > 0}
        sim.simData['dnumc'] = {pop: np.amax(dGIDs[pop]) - np.amin(dGIDs[pop]) for pop in lpop if len(dGIDs[pop]) > 0}

    def setCochCellLocationsX(sim, freqL, freqU, pop, sz, scale):
        # set the cell positions on a line
        if pop not in sim.net.pops: return
        offset = sim.simData['dminID'][pop]
        ncellinrange = 0  # number of cochlear cells with center frequency in frequency range represented by this model
        sidx = -1
        for idx, cf in enumerate(sim.net.params.cf):
            if cf >= freqL and cf <= freqU:
                if sidx == -1: sidx = idx  # start index
                ncellinrange += 1
        if sidx > -1: offset += sidx
        # print('setCochCellLocations: sidx, offset, ncellinrange = ', sidx, offset, ncellinrange)
        for c in sim.net.cells:
            if c.gid in sim.net.pops[pop].cellGids:
                cf = sim.net.params.cf[c.gid - sim.simData['dminID'][pop]]
                if cf >= freqL and cf <= freqU:
                    print(c.tags['x'] + 'BEFORE')
                    c.tags['x'] = cellx = scale * (cf - freqL) / (
                                freqU - freqL)
                    print(c.tags['x'] + 'AFTER')
                    c.tags['xnorm'] = cellx / sim.net.params.sizeX  # make sure these values consistent
                    # print('gid,cellx,xnorm,cf=',c.gid,cellx,cellx/netParams.sizeX,cf)
                else:
                    c.tags['x'] = cellx = 100000000  # put it outside range for core
                    c.tags['xnorm'] = cellx / sim.net.params.sizeX  # make sure these values consistent
                c.updateShape()

    def checkCochConns(sim, pop):
        cochGids = []
        cochConns = []

        for cell in sim.net.cells:
            if cell.tags['pop'] == 'cochlea':
                cochGids.append(cell.gid)
        print('Number of Cochlea Cells is ' + str(len(cochGids)))

        for cell in sim.net.cells:
            if cell.tags['pop'] == pop:
                for conn in cell.conns:
                    if conn['preGid'] in cochGids:
                        cochConns.append(conn)

        print('Number of Cochlea Conns is ' + str(len(cochConns)))

    def checkTCconnRatio(sim, pop):
        TCConns = []
        L6TCConns = []
        IRETCConns = []
        CochTCConns = []
        for cell in sim.net.cells:
            if cell.tags['pop'] == pop:
                for conn in cell.conns:
                    TCConns.append(conn['preGid'])
        for conn in TCConns:
            if conn in sim.net.pops['CT6'].cellGids:
                L6TCConns.append(conn)
            elif conn in sim.net.pops['IRE'].cellGids:
                IRETCConns.append(conn)
            elif conn in sim.net.pops['cochlea'].cellGids:
                CochTCConns.append(conn)
        pctCoch = (len(CochTCConns) / len(TCConns)) * 100
        pctIRE = (len(IRETCConns) / len(TCConns)) * 100
        pctL6 = (len(L6TCConns) / len(TCConns)) * 100

        print(str(pctCoch) + '% of TC Conns are from Cochlea')
        print(str(pctIRE) + '% of TC Conns are from IRE')
        print(str(pctL6) + '% of TC Conns are from CT6')


################## Scrap for resampling if needed later ##################################################
'''
# num_samples = len(stim_data)
# new_num_samples = int(num_samples * 1000/ 20000)
# resampled_data = signal.resample(stim_data, new_num_samples)
'''

