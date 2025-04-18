"""
This script reads a batch simulation result folder,
extracts the OU parameters from the json config files,
calculates the firing rates and CVs from pkl files,
and saves the results to a CSV file.

Each table row corresponds to a single batch job.

"""

import json
import os
from pathlib import Path
import pickle

import pandas as pd

import data_proc_utils as proc_utils
import netpyne_res_parse_utils as parse_utils


# Experiment name
exp_name = 'its4_10x10_large'

# Time limits for the rate and CV calculation (in seconds)
t_limits = (2, 3)  # in seconds

# Min. number of spikes to use a cell for CV calculation
nspikes_min = 5


# Define the output file path
dirpath_base = (
    Path(__file__).resolve().parents[2] /  # two levels above this script
    'exp_results' / exp_name
)

cfg_files = list(dirpath_base.rglob('*_cfg.json'))
data_files = [file.with_name(file.stem.replace('_cfg', '_data') + '.pkl')
              for file in cfg_files]

res = []

for n, (cfg_file, data_file) in enumerate(zip(cfg_files, data_files)):
    #print(cfg_file)

    # Get OU params from config json file
    with open(cfg_file, 'r') as fid:
        cfg = json.load(fid)
    ou_mean = cfg['simConfig']['OUamp']
    ou_std = cfg['simConfig']['OUstd']
    print(f'ou_mean: {ou_mean}, ou_std: {ou_std}')

    # Load sim result
    with open(data_file, 'rb') as fid:
        sim_result = pickle.load(fid)

    ncells = parse_utils.get_net_size(sim_result)

    # Calculate firing rates
    spikes = parse_utils.get_net_spikes(sim_result)
    rates = proc_utils.calc_net_rates(spikes, time_limits=t_limits,
                                      ncells=ncells)

    # Calculate CVs
    cell_spikes = parse_utils.get_net_spikes(sim_result,
                                             combine_cells=False)
    cvs = proc_utils.calc_net_cvs(cell_spikes, time_limits=t_limits,
                                  nspikes_min=nspikes_min, avg_result=True)

    entry = {'ou_mean': ou_mean, 'ou_std': ou_std,
             'rate': rates, 'cv': cvs}
    res.append(entry)

# Create a DataFrame from the results
columns = ['ou_mean', 'ou_std']
pop_names = list(res[0]['rate'].keys())
for pop in pop_names:
    columns.extend([f'{pop}_r', f'{pop}_cv'])

data = []
for entry in res:
    row = [entry['ou_mean'], entry['ou_std']]
    for pop in pop_names:
        row.append(entry['rate'][pop])
        row.append(entry['cv'][pop])
    data.append(row)

df = pd.DataFrame(data, columns=columns)

# Save the DataFrame to a CSV file
fpath_res = dirpath_base / 'batch_result.csv'
df.to_csv(fpath_res, index=False)
