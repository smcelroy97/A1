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
#from analysis.ou_tuning.xr_utils import iter_xr_slices_along_dims

from batch_params import BATCH_PARAMS

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
        f'exp_oumean_'
        f'{BATCH_PARAMS["ou_mean_range"][0] * 100}_'
        f'{BATCH_PARAMS["ou_mean_range"][1] * 100}_'
        f'oustd_{BATCH_PARAMS["ou_std"] * 100}_'
        f'npts_{BATCH_PARAMS["num_ou_points"]}_'
        f't0_{BATCH_PARAMS["tcalc_min"]}'
    )
    dirpath_comb = dirpath_exp / exp_name_sub / 'combined'
    os.makedirs(dirpath_comb, exist_ok=True)

    # Extract (param_grid -> job_id) xarray from cfg folder
    job_idx_xr = batch_utils.extract_batch_params_to_xr(
        dirpath_exp / exp_name_sub / 'cfg',
        cfg_param_fields={'ou_mean': 'ou_mean'},
        fname_cfg_templ='cfg_*.json',
        job_pos_in_fname=1
    )
    job_idx_xr.to_netcdf(dirpath_comb / 'job_idx.nc')
    #print(job_idx_xr)
    #print()

    pops = [BATCH_PARAMS['pop_name']]

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

    ou_mean_vals = job_idx_xr.coords['ou_mean'].values

    for ou_mean in ou_mean_vals:
        # Read rates for job result
        job_id = job_idx_xr.sel(ou_mean=ou_mean).item()
        fpath_res = _get_fpath_by_templ(dirpath_exp / exp_name_sub / 'results',
                                        f'result_{job_id:05d}*.json')
        with open(fpath_res, 'r') as fid:
            sim_res = json.load(fid)
        
        # Store to the output
        for pop in pops:
            cc = {'pop': pop, 'job': job_id}
            X['ou_mean'].loc[cc] = ou_mean
            X['ou_std'].loc[cc] = BATCH_PARAMS['ou_std']
            X['rate'].loc[cc] = sim_res['rates'][pop]
            X['cv'].loc[cc] = sim_res['cvs'][pop]
            X['v_med_max'].loc[cc] = sim_res['v_med_max'][pop]
            X['v_med_min'].loc[cc] = sim_res['v_med_min'][pop]

    # Save the combined result
    X.to_netcdf(dirpath_comb / 'rates_cvs_all.nc')
    #print(X)

    # Plot rate vs. ou_mean
    pop = BATCH_PARAMS['pop_name']
    ou_mean = X['ou_mean'].sel(pop=pop).values * 100
    rr = X['rate'].sel(pop=pop).values
    cv = X['cv'].sel(pop=pop).values
    v_med_max = X['v_med_max'].sel(pop=pop).values
    v_med_min = X['v_med_min'].sel(pop=pop).values
    #mask = ~np.isnan(cv)
    mask = np.full_like(rr, True, dtype=bool)
    plt.figure()
    plt.subplot(2, 2, 1)
    plt.plot(ou_mean[mask], rr[mask], '.-')
    #plt.xlabel('ou_mean * 100')
    plt.title(f'Firing rate, {pop}')
    plt.subplot(2, 2, 2)
    plt.plot(ou_mean[mask], cv[mask], '.-')
    #plt.xlabel('ou_mean * 100')
    plt.title(f'CV, {pop}')
    plt.subplot(2, 2, 3)
    plt.plot(ou_mean[mask], v_med_max[mask], '.-')
    plt.xlabel('ou_mean * 100')
    plt.title(f'Max. V median, {pop}')
    plt.subplot(2, 2, 4)
    plt.plot(ou_mean[mask], v_med_min[mask], '.-')
    plt.xlabel('ou_mean * 100')
    plt.title(f'Min. V median, {pop}')
    plt.savefig(dirpath_comb / 'rates_cvs.png', dpi=300)


if __name__ == '__main__':
    exp_name = 'batch_i_ourange_unconn_state1_mech1_nosub_wmult_0.25/pt5b'
    post_batch(exp_name)
