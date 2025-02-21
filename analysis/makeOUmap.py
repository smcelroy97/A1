def makeOUmap(batch_dir):
    import os
    import pickle
    import pandas as pd
    from netpyne import sim
    for file in os.listdir(batch_dir):
        if file.endswith('_data.pkl') or file.endswith('_data.json'):  # make sure you only load output data
            sim.initialize()
            all = sim.loadAll(os.path.join(base_dir, file), instantiate=False)  # Valery did this and fixed some problems, not sure why necessary
            fname = file[0:-9]  # Create filename (can change to whatever)

            avgRates = sim.analysis.popAvgRates(tranges=[2000, 3000], show=False)
            figs, spikesDict = sim.analysis.plotSpikeStats(stats=['isicv', 'rate'], timeRange=[2000, 3000], saveFig=False, showFig=False, show=False)

            ouamp_list = sim.cfg.OUamp if isinstance(sim.cfg.OUamp, (list, np.ndarray)) else [sim.cfg.OUamp]
            oustd_list = sim.cfg.OUstd if isinstance(sim.cfg.OUstd, (list, np.ndarray)) else [sim.cfg.OUstd]

            rate_dataframes = pop_dataframes.get('rate', {pop: pd.DataFrame(index=oustd_list, columns=ouamp_list) for pop in sim.cfg.allpops})
            isicv_dataframes = pop_dataframes.get('isicv', {pop: pd.DataFrame(index=oustd_list, columns=ouamp_list) for pop in sim.cfg.allpops})

            for df in rate_dataframes.values():
                df.index.name = 'OUstd'
                df.columns.name = 'OUamp'
            for df in isicv_dataframes.values():
                df.index.name = 'OUstd'
                df.columns.name = 'OUamp'

            for idx, pop in enumerate(sim.cfg.allpops):
                for ouamp in ouamp_list:
                    for oustd in oustd_list:
                        rate_dataframes[pop].at[oustd, ouamp] = avgRates[pop]
                        isicv_dataframes[pop].at[oustd, ouamp] = np.mean(spikesDict['statData'][idx + 1])

            # Sort the DataFrames by index
            for df in rate_dataframes.values():
                df.sort_index(inplace=True)
            for df in isicv_dataframes.values():
                df.sort_index(inplace=True)

            return rate_dataframes, isicv_dataframes

rate_df, isicv_df = makeOUmap('simOutput/v45_batch15')

with open('OUmapping.pkl', 'wb') as file:
    pickle.dump({'rate': rate_df, 'isicv': isicv_df}, file)