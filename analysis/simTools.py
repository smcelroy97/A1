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
class simTools:
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


    def plot_PSD(data, save_dir, figsize = (20,20)):
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
                rate = count / bin_duration  # * 1000  # Convert to Hz
                pop_firing_rates.append(rate)

            # Store the firing rates for the current population
            firing_rates[pop] = pop_firing_rates
        # Plot the firing rates
        plt.figure()
        for pop, rates in firing_rates.items():
            plt.plot(rates, label=pop)
        plt.xlabel('Bin Index')
        plt.ylabel('Firing rate')
        plt.xticks(range(0, (len(bin_start_times))))
        plt.legend()
        plt.savefig(save_dir + '_MUA.png')


#####################################################
#    Funcitons for editing a network after cells and conns are made     #
#####################################################
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






################## Scrap for resampling if needed later ##################################################
# num_samples = len(stim_data)
# new_num_samples = int(num_samples * 1000/ 20000)
# resampled_data = signal.resample(stim_data, new_num_samples)
