import json
from pathlib import Path
import pickle

import numpy as np
import pandas as pd

import data_proc_utils as proc_utils
import netpyne_res_parse_utils as parse_utils


dirpath_base = Path(r'D:\WORK\Salvador\repo\A1_OUinp\simulations\exp_results_common'
                    r'\batch_ougrid_pv_0')

cfg_files = list(dirpath_base.rglob('*_cfg.json'))
data_files = [file.with_name(file.stem.replace('_cfg', '_data') + '.pkl') for file in cfg_files]

""" for c, d in zip(cfg_files, data_files):
    print(f'cfg: {c}')
    print(f'data: {d}')
    print('') """

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

    t_limits = (2, 3)  # in seconds
    nspikes_min = 3

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

