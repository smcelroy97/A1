from mpi4py import MPI
import pickle
import pandas as pd
import numpy as np
from netpyne import sim
import os
import spike_utils

# MPI setup
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
batch = 'v45_batch18'

# Directory containing simulation data
sim_dir = str("simOutput/" + batch + "/")
all_files = sorted([f for f in os.listdir(sim_dir) if f.endswith("_data.pkl")])
files_per_rank = np.array_split(all_files, size)


# Helper function to compute firing rate and ISICV
def compute_metrics(simResults, trange = [2000, 3000]):

    rate_dict = {}
    isicv_dict = {}
    pop_spikes_combo = {}
    pop_spikes = {}
    for pop in simResults['net']['pops']:
        pop_spikes_combo[pop] = spike_utils.get_pop_spikes(simResults, pop, combine_cells=True, t0 = trange[0]/1000, ms = True)
        pop_spikes[pop] = spike_utils.get_pop_spikes(simResults, pop, combine_cells=False, t0 = trange[0]/1000, ms = True)

    for pop in pop_spikes_combo:
        rate_dict[pop] = len(pop_spikes_combo[pop])/((trange[1]-trange[0]) / 1000 * len(simResults['net']['pops'][pop]['cellGids']))

    for pop in pop_spikes:
        isicvs = []
        for cell in pop_spikes[pop]:
            isi  = np.diff(cell)
            if len(isi) > 1:
                isicv = np.nanstd(isi)/np.nanmean(isi)
            else:
                isicv = np.nan
            isicvs.append(isicv)
        isicv_dict[pop] = np.nanmean(isicvs)

    return rate_dict, isicv_dict


# Rank-specific processing
rate_dicts, isicv_dicts = [], []
for file in files_per_rank[rank]:
    filepath = os.path.join(sim_dir, file)

    with open(filepath, 'rb') as file:
        simResults = pickle.load(file)


    rate_dict, isicv_dict = compute_metrics(simResults)

    rate_dicts.append((simResults['simConfig']['OUstd'], simResults['simConfig']['OUamp'], rate_dict))
    isicv_dicts.append((simResults['simConfig']['OUstd'], simResults['simConfig']['OUamp'], isicv_dict))

# Gather results
all_rate_dicts = comm.gather(rate_dicts, root=0)
all_isicv_dicts = comm.gather(isicv_dicts, root=0)

if rank == 0:
    final_rate_dict = {}
    final_isicv_dict = {}

    # Organizing rate and ISICV into dictionaries
    for d_list in all_rate_dicts:
        for OUstd, OUamp, d in d_list:
            for pop, val in d.items():
                if pop not in final_rate_dict:
                    final_rate_dict[pop] = {}
                final_rate_dict[pop][(OUstd, OUamp)] = val

    for d_list in all_isicv_dicts:
        for OUstd, OUamp, d in d_list:
            for pop, val in d.items():
                if pop not in final_isicv_dict:
                    final_isicv_dict[pop] = {}
                final_isicv_dict[pop][(OUstd, OUamp)] = val

    # Convert dictionaries to structured DataFrames
    for pop in final_rate_dict:
        df = pd.DataFrame.from_dict(final_rate_dict[pop], orient='index')
        df.index = pd.MultiIndex.from_tuples(df.index, names=['OUstd', 'OUamp'])
        final_rate_dict[pop] = df.unstack(level=1).droplevel(0, axis=1)  # Make OUstd the rows, OUamp the columns

    for pop in final_isicv_dict:
        df = pd.DataFrame.from_dict(final_isicv_dict[pop], orient='index')
        df.index = pd.MultiIndex.from_tuples(df.index, names=['OUstd', 'OUamp'])
        final_isicv_dict[pop] = df.unstack(level=1).droplevel(0, axis=1)  # Make OUstd the rows, OUamp the columns

    # Save results
    with open(str("OUmapping" + batch + ".pkl", "wb")) as f:
        pickle.dump({"rate": final_rate_dict, "isicv": final_isicv_dict}, f)

    print(str("Final results saved as OUmapping_" + batch + ".pkl"))
