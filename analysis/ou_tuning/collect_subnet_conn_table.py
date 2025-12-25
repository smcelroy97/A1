import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr


dirpath_cfg = Path('/ddn/niknovikov19/repo/A1_OUinp/exp_configs')
dirpath_res = Path('/ddn/niknovikov19/repo/A1_OUinp/exp_results')

exp_name = 'batch_i_ou_subnet_conn_wmult_0.05_pyr_pv_5s_ramp'


# Read target rates
fpath_target_rates = dirpath_cfg / exp_name / 'frozen_rates.csv'
df_target = pd.read_csv(fpath_target_rates)
pop_names = df_target['pop_name'].to_list()

dirpath_res_exp = dirpath_res / exp_name

# Enumerate results
res_files = list(dirpath_res_exp.rglob('*_result.json'))

# Allocate xarray for the rates
npops, njobs = len(pop_names), len(res_files)
R = xr.DataArray(
    np.full((npops, njobs), np.nan),
    dims=['pop', 'job'],
    coords={'pop': pop_names, 'job': np.arange(njobs)}
)

for n, res_file in enumerate(res_files):
    # Get job id
    job_id = int(res_file.stem.split('_')[-2])
    print(f'Job: {job_id:05d}', flush=True)

    # Load the result
    with open(res_file, 'r') as fid:
        pop_rates = json.load(fid)['rates']
    
    # Remove all pops. whose names contain 'frz'
    pop_rates = {k: v for k, v in pop_rates.items() if 'frz' not in k}

    for pop, r in pop_rates.items():
        R.loc[{'pop': pop, 'job': job_id}] = np.round(r, 1)

# Convert R to pandas DataFrame
df_rates = R.to_pandas()
df_rates.index.name = 'pop'
df_rates.columns.name = 'job'

# Add target rates to the table
df = df_rates.reset_index()
df = df.merge(df_target, left_on='pop', right_on='pop_name')
df.drop(columns='pop_name', inplace=True)
cols = df.columns.tolist()
cols.insert(1, cols.pop(cols.index('target_rate')))
df = df[cols]

# Save the result
dirpath_out = dirpath_res_exp / 'analysis'
os.makedirs(dirpath_out, exist_ok=True)
fpath_out = dirpath_out / 'rates.csv'
df.to_csv(fpath_out)