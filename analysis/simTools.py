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

    def spikeStats(
        include=['eachPop', 'allCells'],
        statDataIn={},
        timeRange=None,
        graphType='boxplot',
        stats=['rate', 'isicv'],
        bins=50,
        histlogy=False,
        histlogx=False,
        histmin=0.0,
        density=False,
        includeRate0=False,
        legendLabels=None,
        normfit=False,
        histShading=True,
        xlim=None,
        popColors={},
        figSize=(6, 8),
        fontSize=12,
        dpi=100,
        saveData=None,
        saveFig=None,
        showFig=True,
        **kwargs
    ):
        """
        Function for/to <short description of `netpyne.analysis.spikes.plotSpikeStats`>

        Parameters
        ----------
        include : list
            Populations and cells to include in the plot.
            **Default:**
            ``['eachPop', 'allCells']`` plots histogram for each population and overall average
            **Options:**
            ``['all']`` plots all cells and stimulations,
            ``['allNetStims']`` plots just stimulations,
            ``['popName1']`` plots a single population,
            ``['popName1', 'popName2']`` plots multiple populations,
            ``[120]`` plots a single cell,
            ``[120, 130]`` plots multiple cells,
            ``[('popName1', 56)]`` plots a cell from a specific population,
            ``[('popName1', [0, 1]), ('popName2', [4, 5, 6])]``, plots cells from multiple populations

        statDataIn : dict
            A pre-computed dictionary of stats data to import.
            **Default:** ``{}``
            **Options:** ``<option>`` <description of option>

        timeRange : list [start, stop]
            Time range to plot.
            **Default:**
            ``None`` plots entire time range
            **Options:** ``<option>`` <description of option>

        graphType : str
            Whether to plot stats using boxplots or histograms.
            **Default:** ``'boxplot'``
            **Options:** ``'histogram'``

        stats : list
            Statistics to plot.
            **Default:** ``['rate', 'isicv']``
            **Options:** ``['rate', 'isicv', 'sync', 'pairsync']``

        bins : int or list
            Number of bins (if int) or edges (if list) for histogram
            **Default:** ``50``
            **Options:** ``<option>`` <description of option>

        histlogy : bool
            <Short description of histlogy>
            **Default:** ``False``
            **Options:** ``<option>`` <description of option>

        histlogx : bool
            Whether to make the x axis logarithmic
            **Default:** ``False``
            **Options:** ``<option>`` <description of option>

        histmin : float
            The minimumum value to include in analyses.
            **Default:** ``0.0``
            **Options:** ``<option>`` <description of option>

        density : bool
            If ``True``, weights values by density
            **Default:** ``False``
            **Options:** ``<option>`` <description of option>

        includeRate0 : bool
            Needs documentation.
            **Default:** ``False``
            **Options:** ``<option>`` <description of option>

        legendLabels : list?
            Needs documentation.
            **Default:** ``None``
            **Options:** ``<option>`` <description of option>

        normfit : bool
            Needs documentation.
            **Default:** ``False``
            **Options:** ``<option>`` <description of option>

        histShading : bool
            Needs documentation.
            **Default:** ``True``
            **Options:** ``<option>`` <description of option>

        xlim : list [min, max]
            Sets the x limits of the plot.
            **Default:** ``None``
            **Options:** ``<option>`` <description of option>

        popColors : dict
            Dictionary with custom color (value) used for each population (key).
            **Default:** ``{}`` uses standard colors
            **Options:** ``<option>`` <description of option>

        figSize : list [width, height]
            Size of figure in inches.
            **Default:** ``(10, 8)``
            **Options:** ``<option>`` <description of option>

        fontSize : int
            Font size on figure.
            **Default:** ``12``
            **Options:** ``<option>`` <description of option>

        dpi : int
            Resolution of figure in dots per inch.
            **Default:** ``100``
            **Options:** ``<option>`` <description of option>

        saveData : bool or str
            Whether and where to save the data used to generate the plot.
            **Default:** ``False``
            **Options:** ``True`` autosaves the data,
            ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.pkl'`` and ``'.json'``

        saveFig : bool or str
            Whether and where to save the figure.
            **Default:** ``False``
            **Options:** ``True`` autosaves the figure,
            ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.png'``, ``'.jpg'``, ``'.eps'``, and ``'.tiff'``

        showFig : bool
            Shows the figure if ``True``.
            **Default:** ``True``
            **Options:** ``<option>`` <description of option>

        kwargs : <type>
            <Short description of kwargs>
            **Default:** *required*

        Returns
        -------

        """

        from netpyne import sim
        from netpyne.analysis.utils import colorList, exception, getCellsInclude, getSpktSpkid, _showFigure, _saveFigData, syncMeasure, _smooth1d

        print('Plotting spike stats...')

        # Set plot style
        colors = []
        params = {
            'axes.labelsize': fontSize,
            'font.size': fontSize,
            'legend.fontsize': fontSize,
            'xtick.labelsize': fontSize,
            'ytick.labelsize': fontSize,
            'text.usetex': False,
        }
        plt.rcParams.update(params)

        xlabels = {
            'rate': 'Rate (Hz)',
            'isicv': 'Irregularity (ISI CV)',
            'sync': 'Synchrony',
            'pairsync': 'Pairwise synchrony',
        }

        # Replace 'eachPop' with list of pops
        if 'eachPop' in include:
            include.remove('eachPop')
            for pop in sim.net.allPops:
                include.append(pop)

        # time range
        if timeRange is None:
            timeRange = [0, sim.cfg.duration]

        for stat in stats:
            # create fig
            fig, ax1 = plt.subplots(figsize=figSize)
            fontsiz = fontSize
            xlabel = xlabels[stat]

            statData = []
            gidsData = []
            ynormsData = []

            # Calculate data for each entry in include
            for iplot, subset in enumerate(include):

                if stat in statDataIn:
                    statData = statDataIn[stat]['statData']
                    gidsData = statDataIn[stat].get('gidsData', [])
                    ynormsData = statDataIn[stat].get('ynormsData', [])

                else:
                    cells, cellGids, netStimLabels = getCellsInclude([subset])
                    numNetStims = 0

                    # Select cells to include
                    if len(cellGids) > 0:
                        try:
                            spkinds, spkts = list(
                                zip(
                                    *[
                                        (spkgid, spkt)
                                        for spkgid, spkt in zip(sim.simData['spkid'], sim.simData['spkt'])
                                        if spkgid in cellGids
                                    ]
                                )
                            )
                        except:
                            spkinds, spkts = [], []
                    else:
                        spkinds, spkts = [], []

                    # Add NetStim spikes
                    spkts, spkinds = list(spkts), list(spkinds)
                    numNetStims = 0
                    if 'stims' in sim.simData:
                        for netStimLabel in netStimLabels:
                            netStimSpks = [
                                spk
                                for cell, stims in sim.simData['stims'].items()
                                for stimLabel, stimSpks in stims.items()
                                for spk in stimSpks
                                if stimLabel == netStimLabel
                            ]
                            if len(netStimSpks) > 0:
                                lastInd = max(spkinds) if len(spkinds) > 0 else 0
                                spktsNew = netStimSpks
                                spkindsNew = [lastInd + 1 + i for i in range(len(netStimSpks))]
                                spkts.extend(spktsNew)
                                spkinds.extend(spkindsNew)
                                numNetStims += 1
                    try:
                        spkts, spkinds = list(
                            zip(
                                *[
                                    (spkt, spkind)
                                    for spkt, spkind in zip(spkts, spkinds)
                                    if timeRange[0] <= spkt <= timeRange[1]
                                ]
                            )
                        )
                    except:
                        pass

                    # if scatter get gids and ynorm
                    if graphType == 'scatter':
                        if includeRate0:
                            gids = cellGids
                        else:
                            gids = set(spkinds)
                        ynorms = [sim.net.allCells[int(gid)]['tags']['ynorm'] for gid in gids]

                        gidsData.insert(0, gids)
                        ynormsData.insert(0, ynorms)

                    # rate stats
                    if stat == 'rate':
                        toRate = 1e3 / (timeRange[1] - timeRange[0])
                        if includeRate0:
                            rates = (
                                [spkinds.count(gid) * toRate for gid in cellGids]
                                if len(spkinds) > 0
                                else [0] * len(cellGids)
                            )  # cellGids] #set(spkinds)]
                        else:
                            rates = (
                                [spkinds.count(gid) * toRate for gid in set(spkinds)] if len(spkinds) > 0 else [0]
                            )  # cellGids] #set(spkinds)]
                        statData.append(rates)

                    # Inter-spike interval (ISI) coefficient of variation (CV) stats
                    elif stat == 'isicv':
                        import numpy as np

                        spkmat = [[spkt for spkind, spkt in zip(spkinds, spkts) if spkind == gid] for gid in set(spkinds)]
                        isimat = [[t - s for s, t in zip(spks, spks[1:])] for spks in spkmat if len(spks) > 10]
                        isicv = [np.std(x) / np.mean(x) if len(x) > 0 else 0 for x in isimat]  # if len(x)>0]
                        statData.append(isicv)

                    # synchrony
                    elif stat in ['sync', 'pairsync']:
                        try:
                            import pyspike
                            import numpy as np
                        except:
                            print(
                                "Error: plotSpikeStats() requires the PySpike python package \
                                to calculate synchrony (try: pip install pyspike)"
                            )
                            return 0

                        spkmat = [
                            pyspike.SpikeTrain([spkt for spkind, spkt in zip(spkinds, spkts) if spkind == gid], timeRange)
                            for gid in set(spkinds)
                        ]
                        if stat == 'sync':
                            # (SPIKE-Sync measure)' # see http://www.scholarpedia.org/article/Measures_of_spike_train_synchrony
                            syncMat = [pyspike.spike_sync(spkmat)]
                            # graphType = 'bar'
                        elif stat == 'pairsync':
                            # (SPIKE-Sync measure)' # see http://www.scholarpedia.org/article/Measures_of_spike_train_synchrony
                            syncMat = np.mean(pyspike.spike_sync_matrix(spkmat), 0)

                        statData.append(syncMat)

                colors.append(
                    popColors[subset] if subset in popColors else colorList[iplot % len(colorList)]
                )  # colors in inverse order

            # if 'allCells' included make it black
            if include[0] == 'allCells':
                # if graphType == 'boxplot':
                del colors[0]
                colors.insert(0, (0.5, 0.5, 0.5))  #
                # colors.insert(len(include), (0.5,0.5,0.5))  #

            # boxplot
            if graphType == 'boxplot':
                meanpointprops = dict(marker=(5, 1, 0), markeredgecolor='black', markerfacecolor='white')
                labels = legendLabels if legendLabels else include
                bp = plt.boxplot(
                    statData[::-1],
                    labels=labels[::-1],
                    notch=False,
                    sym='k+',
                    meanprops=meanpointprops,
                    whis=1.5,
                    widths=0.6,
                    vert=False,
                    showmeans=True,
                    patch_artist=True,
                )  # labels[::-1]
                plt.xlabel(xlabel, fontsize=fontsiz)
                plt.ylabel('Population', fontsize=fontsiz)

                icolor = 0
                borderColor = 'k'
                for i in range(0, len(bp['boxes'])):
                    icolor = i
                    bp['boxes'][i].set_facecolor(colors[::-1][icolor])
                    bp['boxes'][i].set_linewidth(2)
                    # we have two whiskers!
                    bp['whiskers'][i * 2].set_color(borderColor)
                    bp['whiskers'][i * 2 + 1].set_color(borderColor)
                    bp['whiskers'][i * 2].set_linewidth(2)
                    bp['whiskers'][i * 2 + 1].set_linewidth(2)
                    bp['medians'][i].set_color(borderColor)
                    bp['medians'][i].set_linewidth(3)
                    # for f in bp['fliers']:
                    #    f.set_color(colors[icolor])
                    #    print f
                    # and 4 caps to remove
                    for c in bp['caps']:
                        c.set_color(borderColor)
                        c.set_linewidth(2)

                ax = plt.gca()
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.get_xaxis().tick_bottom()
                ax.get_yaxis().tick_left()
                ax.tick_params(axis='x', length=0)
                ax.tick_params(axis='y', direction='out')
                ax.grid(axis='x', color="0.9", linestyle='-', linewidth=1)
                ax.set_axisbelow(True)
                if xlim:
                    ax.set_xlim(xlim)

            # histogram
            elif graphType == 'histogram':
                import numpy as np

                nmax = 0
                pdfmax = 0
                binmax = 0
                for i, data in enumerate(statData):  # fix
                    if histlogx:
                        histbins = np.logspace(np.log10(histmin), np.log10(max(data)), bins)
                    else:
                        histbins = bins

                    if histmin:  # min value
                        data = np.array(data)
                        data = data[data > histmin]

                    if density:
                        weights = np.ones_like(data) / float(len(data))
                    else:
                        weights = np.ones_like(data)

                    n, binedges, _ = plt.hist(
                        data, bins=histbins, histtype='step', color=colors[i], linewidth=2, weights=weights
                    )  # , normed=1)#, normed=density)# weights=weights)
                    if histShading:
                        plt.hist(data, bins=histbins, alpha=0.05, color=colors[i], linewidth=0, weights=weights)
                    label = legendLabels[-i - 1] if legendLabels else str(include[-i - 1])
                    if histShading:
                        plt.hist(
                            [-10],
                            bins=histbins,
                            fc=((colors[i][0], colors[i][1], colors[i][2], 0.05)),
                            edgecolor=colors[i],
                            linewidth=2,
                            label=label,
                        )
                    else:
                        plt.hist([-10], bins=histbins, fc=((1, 1, 1), 0), edgecolor=colors[i], linewidth=2, label=label)
                    nmax = max(nmax, max(n))
                    binmax = max(binmax, binedges[-1])
                    if histlogx:
                        plt.xscale('log')

                    if normfit:

                        def lognorm(meaninput, stdinput, binedges, n, popLabel, color):
                            from scipy import stats

                            M = float(meaninput)  # Geometric mean == median
                            s = float(stdinput)  # Geometric standard deviation
                            mu = np.log10(M)  # Mean of log(X)
                            sigma = np.log10(s)  # Standard deviation of log(X)
                            shape = sigma  # Scipy's shape parameter
                            scale = np.power(10, mu)  # Scipy's scale parameter
                            x = [
                                (binedges[i] + binedges[i + 1]) / 2.0 for i in range(len(binedges) - 1)
                            ]  # np.linspace(histmin, 30, num=400) # values for x-axis
                            pdf = stats.lognorm.pdf(x, shape, loc=0, scale=scale)  # probability distribution
                            R, p = scipy.stats.pearsonr(n, pdf)
                            print(
                                '    Pop %s rate: mean=%f, std=%f, lognorm mu=%f, lognorm sigma=%f, R=%.2f (p-value=%.2f)'
                                % (popLabel, M, s, mu, sigma, R, p)
                            )
                            plt.semilogx(x, pdf, color=color, ls='dashed')
                            return pdf

                        fitmean = np.mean(data)
                        fitstd = np.std(data)
                        pdf = lognorm(fitmean, fitstd, binedges, n, label, colors[i])
                        pdfmax = max(pdfmax, max(pdf))
                        nmax = max(nmax, pdfmax)

                        # check normality of distribution
                        # W, p = scipy.stats.shapiro(data)
                        # print 'Pop %s rate: mean = %f, std = %f, normality (Shapiro-Wilk test) = %f, p-value = %f' % (include[i], mu, sigma, W, p)

                plt.xlabel(xlabel, fontsize=fontsiz)
                plt.ylabel('Probability of occurrence' if density else 'Frequency', fontsize=fontsiz)
                xmax = binmax
                plt.xlim(histmin, xmax)
                plt.ylim(0, 1.1 * nmax if density else np.ceil(1.1 * nmax))  # min(n[n>=0]), max(n[n>=0]))
                plt.legend(fontsize=fontsiz)

                # if xlim: ax.set_xlim(xlim)

            # scatter
            elif graphType == 'scatter':
                from scipy import stats

                for i, (ynorms, data) in enumerate(zip(ynormsData, statData)):
                    mean, binedges, _ = stats.binned_statistic(ynorms, data, 'mean', bins=bins)
                    median, binedges, _ = stats.binned_statistic(ynorms, data, 'median', bins=bins)
                    # p25 = lambda x: np.percentile(x, 25)
                    # p75 = lambda x: np.percentile(x, 75)

                    std, binedges, _ = stats.binned_statistic(ynorms, data, 'std', bins=bins)
                    # per25, binedges, _ = stats.binned_statistic(ynorms, data, p25, bins=bins)
                    # per75, binedges, _ = stats.binned_statistic(ynorms, data, p75, bins=bins)

                    label = legendLabels[-i - 1] if legendLabels else str(include[-i - 1])
                    if kwargs.get('differentColor', None):
                        threshold = kwargs['differentColor'][0]
                        newColor = kwargs['differentColor'][1]  #
                        plt.scatter(
                            ynorms[:threshold],
                            data[:threshold],
                            color=[6 / 255.0, 8 / 255.0, (64 + 30) / 255.0],
                            label=label,
                            s=2,
                        )  # , [0/255.0,215/255.0,255/255.0], [88/255.0,204/255.0,20/255.0]
                        plt.scatter(
                            ynorms[threshold:], data[threshold:], color=newColor, alpha=0.2, s=2
                        )  # [88/255.0,204/255.0,20/255.0]
                    else:
                        plt.scatter(
                            ynorms, data, color=[0 / 255.0, 215 / 255.0, 255 / 255.0], label=label, s=2
                        )  # [88/255.0,204/255.0,20/255.0]
                    binstep = binedges[1] - binedges[0]
                    bincenters = [b + binstep / 2 for b in binedges[:-1]]
                    plt.errorbar(
                        bincenters,
                        mean,
                        yerr=std,
                        color=[6 / 255.0, 70 / 255.0, 163 / 255.0],
                        fmt='o-',
                        capthick=1,
                        capsize=5,
                    )  # [44/255.0,53/255.0,127/255.0]
                    # plt.errorbar(bincenters, mean, yerr=[mean-per25,per75-mean], fmt='go-',capthick=1, capsize=5)
                ylims = plt.ylim()
                plt.ylim(0, ylims[1])
                plt.xlabel('normalized y location (um)', fontsize=fontsiz)
                # plt.xlabel('avg rate (Hz)', fontsize=fontsiz)
                plt.ylabel(xlabel, fontsize=fontsiz)
                plt.legend(fontsize=fontsiz)

            try:
                plt.tight_layout()
            except:
                pass

            # save figure data
            if saveData:
                figData = {
                    'include': include,
                    'statData': statData,
                    'timeRange': timeRange,
                    'saveData': saveData,
                    'saveFig': saveFig,
                    'showFig': showFig,
                }

                _saveFigData(figData, saveData, 'spikeStats_' + stat)

            # save figure
            if saveFig:
                if isinstance(saveFig, basestring):
                    filename = saveFig + '_spikeStat_' + graphType + '_' + stat + '.png'
                else:
                    filename = sim.cfg.filename + '_spikeStat_' + graphType + '_' + stat + '.png'
                plt.savefig(filename, dpi=dpi)

            # show fig
            if showFig:
                _showFigure()

        return fig, {'include': include, 'statData': statData, 'gidsData': gidsData, 'ynormsData': ynormsData}



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

