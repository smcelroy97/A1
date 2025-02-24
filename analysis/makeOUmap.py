import os
import pickle
import pandas as pd
from netpyne import sim
import numpy as np

def process_file(file_path):
    sim.initialize()
    sim.loadAll(file_path, instantiate=False)

    if not hasattr(sim.net, 'allCells') or not hasattr(sim.net, 'allPops'):
        print(f"Error: Network object in file {file_path} does not have allCells or allPops attributes")
        return {}, {}

    avgRates = sim.analysis.popAvgRates(tranges=[2000, 3000], show=False)
    result = sim.analysis.plotSpikeStats(stats=['isicv', 'rate'], timeRange=[2000, 3000], saveFig=False, showFig=False, show=False)

    if not isinstance(result, dict):
        print(f"Error in plotSpikeStats for file {file_path}")
        return {}, {}

    spikesDict = result

    ouamp_list = sim.cfg.OUamp if isinstance(sim.cfg.OUamp, (list, np.ndarray)) else [sim.cfg.OUamp]
    oustd_list = sim.cfg.OUstd if isinstance(sim.cfg.OUstd, (list, np.ndarray)) else [sim.cfg.OUstd]

    rate_dataframes = {}
    isicv_dataframes = {}

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

    return rate_dataframes, isicv_dataframes

def makeOUmap(batch_dir):
    files = [os.path.join(batch_dir, file) for file in os.listdir(batch_dir) if file.endswith('_data.pkl') or file.endswith('_data.json')]

    final_rate_dataframes = {}
    final_isicv_dataframes = {}

    for file in files:
        rate_dataframes, isicv_dataframes = process_file(file)
        for pop in rate_dataframes:
            if pop not in final_rate_dataframes:
                final_rate_dataframes[pop] = rate_dataframes[pop]
                final_isicv_dataframes[pop] = isicv_dataframes[pop]
            else:
                final_rate_dataframes[pop] = final_rate_dataframes[pop].add(rate_dataframes[pop], fill_value=0)
                final_isicv_dataframes[pop] = final_isicv_dataframes[pop].add(isicv_dataframes[pop], fill_value=0)

    for df in final_rate_dataframes.values():
        df.sort_index(inplace=True)
    for df in final_isicv_dataframes.values():
        df.sort_index(inplace=True)

    with open('OUmapping.pkl', 'wb') as file:
        pickle.dump({'rate': final_rate_dataframes, 'isicv': final_isicv_dataframes}, file)

if __name__ == '__main__':
    makeOUmap('simOutput/v45_batch15')