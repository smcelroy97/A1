import json
import os
from pathlib import Path
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

dirpath_repo_root = Path(__file__).resolve().parents[3]
dirpath_self = Path(__file__).resolve().parent
sys.path.append(str(dirpath_repo_root))
sys.path.append(str(dirpath_self))

from analysis.ou_tuning import batch_utils

from batch_params import BATCH_PARAMS, _select_ou_from_range

matplotlib.use('Agg', force=True)


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
    exp_name_sub = (
        f'exp_npts_{BATCH_PARAMS["num_ou_points"]}_'
        f'std0_{(100 * BATCH_PARAMS["ou_std_intercept"]):.01f}_'
        f'kstd_{(100 * BATCH_PARAMS["ou_std_mean_ratio"]):.01f}'
    )
    dirpath_comb = dirpath_exp / exp_name_sub / 'combined'
    os.makedirs(dirpath_comb, exist_ok=True)

    # Extract (param_grid -> job_id) xarray from cfg folder
    job_idx_xr = batch_utils.extract_batch_params_to_xr(
        dirpath_exp / exp_name_sub / 'cfg',
        cfg_param_fields={'ou_range_pos': 'ou_range_pos'},
        fname_cfg_templ='cfg_*.json',
        job_pos_in_fname=1
    )
    job_idx_xr.to_netcdf(dirpath_comb / 'job_idx.nc')
    #print(job_idx_xr)
    #print()

    # Read OU ranges for the pops. from csv file
    ou_ranges = pd.read_csv(dirpath_exp_cfg / 'ou_mean_ranges.csv')
    ou_ranges = ou_ranges.set_index('pop_name')

    pops = ['VIP2', 'VIP3', 'VIP4', 'VIP5A', 'VIP5B', 'VIP6']

    # Allocate output
    Z = xr.DataArray(
        data=np.full([len(pops), len(job_idx_xr)], np.nan),
        dims=['pop', 'job'],
        coords={'pop': pops, 'job': np.sort(job_idx_xr.values)}
    )
    X = xr.Dataset({
        v: Z.copy()
        for v in ['rate', 'cv', 'v_med_max', 'v_med_min', 'ou_mean', 'ou_std']
    })

    for ou_range_pos in job_idx_xr.ou_range_pos.values:
        # Read rates for job result
        job_id = job_idx_xr.sel(ou_range_pos=ou_range_pos).item()
        fpath_res = _get_fpath_by_templ(dirpath_exp / exp_name_sub / 'results',
                                        f'result_{job_id:05d}*.json')
        with open(fpath_res, 'r') as fid:
            sim_res = json.load(fid)

        # Select OU from the range for every pop.
        ou_pop_inputs = _select_ou_from_range(ou_ranges, ou_range_pos,
            ou_std_mean_ratio=0, ou_std_intercept=0)
        
        # Store to the output
        for pop in pops:
            cc = {'pop': pop, 'job': job_id}
            X['ou_mean'].loc[cc] = ou_pop_inputs[pop]['ou_mean']
            X['ou_std'].loc[cc] = ou_pop_inputs[pop]['ou_std']
            X['rate'].loc[cc] = sim_res['rates'][pop]
            X['cv'].loc[cc] = sim_res['cvs'][pop]
            X['v_med_max'].loc[cc] = sim_res['v_med_max'][pop]
            X['v_med_min'].loc[cc] = sim_res['v_med_min'][pop]

    # Save the combined result
    X.to_netcdf(dirpath_comb / 'rates_cvs_all.nc')
    #print(X)

    # Plot rate vs. ou_mean
    for pop in pops:
        ou_mean = X['ou_mean'].sel(pop=pop).values * 100
        rr = X['rate'].sel(pop=pop).values
        cv = X['cv'].sel(pop=pop).values
        v_med_max = X['v_med_max'].sel(pop=pop).values
        v_med_min = X['v_med_min'].sel(pop=pop).values
        plt.figure(111)
        plt.clf()
        plt.subplot(2, 2, 1)
        plt.plot(ou_mean, rr, '.-')
        plt.xlim(ou_mean.min(), ou_mean.max())
        #plt.xlabel('ou_mean * 100')
        plt.title(f'Firing rate, {pop}')
        plt.subplot(2, 2, 2)
        plt.plot(ou_mean, cv, '.-')
        plt.xlim(ou_mean.min(), ou_mean.max())
        #plt.xlabel('ou_mean * 100')
        plt.title(f'CV, {pop}')
        plt.subplot(2, 2, 3)
        plt.plot(ou_mean, v_med_max, '.-')
        plt.xlim(ou_mean.min(), ou_mean.max())
        plt.xlabel('ou_mean * 100')
        plt.title(f'Max. V median, {pop}')
        plt.subplot(2, 2, 4)
        plt.plot(ou_mean, v_med_min, '.-')
        plt.xlim(ou_mean.min(), ou_mean.max())
        plt.xlabel('ou_mean * 100')
        plt.title(f'Min. V median, {pop}')
        plt.savefig(dirpath_comb / f'result_{pop}.png', dpi=300)


if __name__ == '__main__':
    exp_name = 'batch_i_ouslice_unconn_state_1_nosub/vip_wmult_0.1'
    post_batch(exp_name)
