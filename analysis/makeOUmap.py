from mpi4py import MPI
import pickle
import pandas as pd
import numpy as np
from netpyne import sim
import os

# MPI setup
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Directory containing simulation data
sim_dir = "simOutput/v45_batch15"
all_files = sorted([f for f in os.listdir(sim_dir) if f.endswith("_data.pkl")])
files_per_rank = np.array_split(all_files, size)


# Helper function to compute firing rate and ISICV
def compute_metrics(spike_times, spike_gids, pops, t_start=2000, t_end=3000):
    rate_dict = {pop: 0.0 for pop in pops}
    isicv_dict = {pop: None for pop in pops}

    pop_gids = {pop: list(pops[pop].cellGids) for pop in pops}
    pop_spikes = {pop: [] for pop in pops}

    for gid, spk_time in zip(spike_gids, spike_times):
        if not isinstance(spk_time, list):
            spk_time = [spk_time]  # Convert single float to list
        spk_time = [t for t in spk_time if t_start <= t <= t_end]  # Apply time filtering

        for pop, gids in pop_gids.items():
            if gid in gids:
                pop_spikes[pop].extend(spk_time)  # Use the corrected variable

    for pop, spikes in pop_spikes.items():
        if spikes:
            rate_dict[pop] = len(spikes) / ((t_end - t_start) / 1000 * len(pop_gids[pop]))
            isis = np.diff(sorted(spikes))
            if len(isis) > 1:
                isicv_dict[pop] = np.std(isis) / np.mean(isis)

    return rate_dict, isicv_dict


# Rank-specific processing
rate_dicts, isicv_dicts = [], []
for file in files_per_rank[rank]:
    filepath = os.path.join(sim_dir, file)

    data = sim.load(filepath, instantiate=False)

    # Ensure pops and cells are properly instantiated
    sim.net.createPops()
    sim.net.createCells()

    print(f"[DEBUG] Rank {rank}: Type of sim.net.pops = {type(sim.net.pops)}")
    print(f"[DEBUG] Rank {rank}: sim.net.pops keys = {list(sim.net.pops.keys())}")

    if not isinstance(sim.net.pops, dict):
        raise ValueError(f"sim.net.pops is not a dict! Found type {type(sim.net.pops)}")

    spike_times = list(sim.allSimData["spkt"])
    spike_gids = list(sim.allSimData["spkid"])

    if len(spike_times) == 0 or len(spike_gids) == 0:
        raise ValueError(f"No spike data in {file}")

    rate_dict, isicv_dict = compute_metrics(spike_times, spike_gids, sim.net.pops)

    rate_dicts.append((sim.cfg.OUstd, sim.cfg.OUamp, rate_dict))
    isicv_dicts.append((sim.cfg.OUstd, sim.cfg.OUamp, isicv_dict))

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
    with open("OUmapping.pkl", "wb") as f:
        pickle.dump({"rate": final_rate_dict, "isicv": final_isicv_dict}, f)

    print("Final results saved as OUmapping.pkl")
