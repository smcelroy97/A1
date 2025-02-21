import os
import pickle
import pandas as pd
from netpyne import sim
import numpy as np

def makeOUmap(batch_dir):
    rate_dataframes = {}
    isicv_dataframes = {}

    for file in os.listdir(batch_dir):
        if file.endswith('_data.pkl') or file.endswith('_data.json'):
            sim.initialize()
            all = sim.loadAll(os.path.join(batch_dir, file), instantiate=False)

            avgRates = sim.analysis.popAvgRates(tranges=[2000, 3000], show=False)
            figs, spikesDict = sim.analysis.plotSpikeStats(stats=['isicv', 'rate'], timeRange=[2000, 3000], saveFig=False, showFig=False, show=False)

            ouamp_list = sim.cfg.OUamp if isinstance(sim.cfg.OUamp, (list, np.ndarray)) else [sim.cfg.OUamp]
            oustd_list = sim.cfg.OUstd if isinstance(sim.cfg.OUstd, (list, np.ndarray)) else [sim.cfg.OUstd]

            for pop in sim.cfg.allpops:
                if pop not in rate_dataframes:
                    rate_dataframes[pop] = pd.DataFrame(index=oustd_list, columns=ouamp_list)
                    isicv_dataframes[pop] = pd.DataFrame(index=oustd_list, columns=ouamp_list)
                    rate_dataframes[pop].index.name = 'OUstd'
                    rate_dataframes[pop].columns.name = 'OUamp'
                    isicv_dataframes[pop].index.name = 'OUstd'
                    isicv_dataframes[pop].columns.name = 'OUamp'

                for ouamp in ouamp_list:
                    for oustd in oustd_list:
                        rate_dataframes[pop].at[oustd, ouamp] = avgRates[pop]
                        isicv_dataframes[pop].at[oustd, ouamp] = np.mean(spikesDict['statData'][sim.cfg.allpops.index(pop) + 1])

    # Sort the DataFrames by index
    for df in rate_dataframes.values():
        df.sort_index(inplace=True)
    for df in isicv_dataframes.values():
        df.sort_index(inplace=True)

    return rate_dataframes, isicv_dataframes

rate_df, isicv_df = makeOUmap('simOutput/v45_batch15')

with open('OUmapping.pkl', 'wb') as file:
    pickle.dump({'rate': rate_df, 'isicv': isicv_df}, file)