import json
import os
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

dirpath_repo_root = Path(__file__).resolve().parents[3]
sys.path.append(str(dirpath_repo_root))

from analysis.ou_tuning import batch_utils
#from analysis.ou_tuning.xr_utils import iter_xr_slices_along_dims

from batch_params import _select_ou_from_range


def _get_fpath_by_templ(dirpath: Path, fname_templ: str) -> str:
    files = list(dirpath.glob(fname_templ))
    if len(files) != 1:
        print(f'Path: {dirpath}')
        print(f'File: {fname_templ}')
        raise RuntimeError('Should be exactly one filename match')
    return files[0]


def post_batch(exp_name):
    dirpath_exp_cfg = dirpath_repo_root / 'exp_configs' / exp_name
    dirpath_exp = dirpath_repo_root / 'exp_results' / exp_name

    # Create folder for combined batch results
    dirpath_comb = dirpath_exp / 'combined'
    os.makedirs(dirpath_comb, exist_ok=True)

    # Extract (param_grid -> job_id) xarray from cfg folder
    job_idx_xr = batch_utils.extract_batch_params_to_xr(
        dirpath_exp / 'cfg',
        cfg_param_fields={'ou_range_pos': 'ou_range_pos'},
        fname_cfg_templ='cfg_*.json',
        job_pos_in_fname=1
    )
    job_idx_xr.to_netcdf(dirpath_comb / 'job_idx.nc')

    # Read OU ranges for the pops. from csv file
    ou_ranges = pd.read_csv(dirpath_exp_cfg / 'ou_mean_ranges.csv')
    ou_ranges = ou_ranges.set_index('pop_name')

    pops = ['IT2', 'IT3', 'ITP4', 'IT5A', 'IT5B',
            'CT5A', 'CT5B', 'IT6', 'CT6']

    # Allocate output
    Z = xr.DataArray(
        data=np.full([len(pops), len(job_idx_xr)], np.nan),
        dims=['pop', 'job'],
        coords={'pop': pops, 'job': np.sort(job_idx_xr.values)}
    )
    X = xr.Dataset({v: Z.copy() for v in ['rate', 'ou_mean', 'ou_std']})

    for ou_range_pos in job_idx_xr.ou_range_pos.values:
        # Read rates for job result
        job_id = job_idx_xr.sel(ou_range_pos=ou_range_pos).item()
        fpath_res = _get_fpath_by_templ(dirpath_exp / 'results',
                                        f'result_{job_id:05d}*.json')
        with open(fpath_res, 'r') as fid:
            pop_rates = json.load(fid)['rates']

        # Select OU from the range for every pop.
        ou_pop_inputs = _select_ou_from_range(ou_ranges, ou_range_pos,
            ou_std_mean_ratio=0.2, ou_std_intercept=0.002)
        
        # Store to the output
        for pop in pops:
            cc = {'pop': pop, 'job': job_id}
            X['ou_mean'].loc[cc] = ou_pop_inputs[pop]['ou_mean']
            X['ou_std'].loc[cc] = ou_pop_inputs[pop]['ou_std']
            X['rate'].loc[cc] = pop_rates[pop]

    # Save the combined result
    X.to_netcdf(dirpath_comb / 'rates_all.nc')


if __name__ == '__main__':
    exp_name = 'batch_i_ou_subnet/batch_i_ou_subnet_wmult_0.05_pyr_ikdr_mult_3s_6pts'
    post_batch(exp_name)
