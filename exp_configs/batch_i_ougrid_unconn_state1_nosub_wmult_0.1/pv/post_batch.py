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

from batch_params import BATCH_PARAMS, gen_exp_name_sub, select_ou_from_range

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
    exp_name_sub = gen_exp_name_sub()
    dirpath_comb = dirpath_exp / exp_name_sub / 'combined'
    os.makedirs(dirpath_comb, exist_ok=True)

    # Extract (param_grid -> job_id) xarray from cfg folder
    job_idx_xr = batch_utils.extract_batch_params_to_xr(
        dirpath_exp / exp_name_sub / 'cfg',
        cfg_param_fields={'ou_mean_pos': 'ou_mean_pos',
                          'ou_std_pos': 'ou_std_pos'},
        fname_cfg_templ='cfg_*.json',
        job_pos_in_fname=1
    )
    job_idx_xr.to_netcdf(dirpath_comb / 'job_idx.nc')

    pops = ['PV2', 'PV3', 'PV4', 'PV5A', 'PV5B', 'PV6']

    # Allocate output
    npops = len(pops)
    npts_mean = BATCH_PARAMS['num_ou_mean_points']
    npts_std = BATCH_PARAMS['num_ou_std_points']
    Z = xr.DataArray(
        data=np.full([npops, npts_mean, npts_std], np.nan),
        dims=['pop', 'ou_mean_ind', 'ou_std_ind'],
        coords={'pop': pops, 'ou_mean_ind': np.arange(npts_mean),
                'ou_std_ind': np.arange(npts_std)}
    )
    X = {v: Z.copy() for v in ['rate', 'cv', 'v_med_max', 'v_med_min']}
    X['ou_mean'] = xr.DataArray(
        data=np.full([npops, npts_mean], np.nan),
        dims=['pop', 'ou_mean_ind'],
        coords={'pop': pops, 'ou_mean_ind': np.arange(npts_mean)}
    )
    X['ou_std'] = xr.DataArray(
        data=np.full([npops, npts_std], np.nan),
        dims=['pop', 'ou_std_ind'],
        coords={'pop': pops, 'ou_std_ind': np.arange(npts_std)}
    )
    X = xr.Dataset(X)

    for n, ou_mean_pos in enumerate(job_idx_xr.ou_mean_pos.values):
        for m, ou_std_pos in enumerate(job_idx_xr.ou_std_pos.values):
            # Read job result
            job_id = job_idx_xr.sel(ou_mean_pos=ou_mean_pos,
                                    ou_std_pos=ou_std_pos).item()
            fpath_res = _get_fpath_by_templ(dirpath_exp / exp_name_sub / 'results',
                                            f'result_{job_id:05d}*.json')
            with open(fpath_res, 'r') as fid:
                sim_res = json.load(fid)

            # Select OU mean and std from the range for every pop.
            ou_pop_inputs = select_ou_from_range(ou_mean_pos, ou_std_pos)
            
            # Store to the output
            for pop in pops:
                X['ou_mean'].loc[{'pop': pop, 'ou_mean_ind': n}] = (
                    ou_pop_inputs[pop]['ou_mean'])
                X['ou_std'].loc[{'pop': pop, 'ou_std_ind': m}] = (
                    ou_pop_inputs[pop]['ou_std'])
                cc = {'pop': pop, 'ou_mean_ind': n, 'ou_std_ind': m}
                X['rate'].loc[cc] = sim_res['rates'][pop]
                X['cv'].loc[cc] = sim_res['cvs'][pop]
                X['v_med_max'].loc[cc] = sim_res['v_med_max'][pop]
                X['v_med_min'].loc[cc] = sim_res['v_med_min'][pop]

    # Save the combined result
    X.to_netcdf(dirpath_comb / 'rates_cvs_all.nc')

    # Plot result metrics
    for pop in pops:
        ou_mean = X['ou_mean'].sel(pop=pop).values * 100
        ou_std = X['ou_std'].sel(pop=pop).values * 100
        mets_vis = ['rate', 'cv', 'v_med_max', 'v_med_min']
        plt.figure(111)
        plt.clf()
        for n, met in enumerate(mets_vis):
            X_ = X[met].sel(pop=pop).values
            plt.subplot(2, 2, n + 1)
            vmin = 0 if met in ['rate', 'cv'] else None
            vmax = 50 if met == 'rate' else None
            plt.imshow(X_.T, aspect='auto', origin='lower',
                       extent=[ou_mean.min(), ou_mean.max(),
                               ou_std.min(), ou_std.max()],
                       vmin=vmin, vmax=vmax)
            plt.xlim(ou_mean.min(), ou_mean.max())
            plt.ylim(ou_std.min(), ou_std.max())
            plt.xticks([])
            plt.yticks([])
            plt.title(f'{met}, {pop}')
        for n in [3, 4]:   # xlabel, xticks
            plt.subplot(2, 2, n)
            plt.xlabel('ou_mean')
            plt.xticks(np.linspace(ou_mean.min(), ou_mean.max(), 5))
        for n in [1, 3]:   # ylabel, yticks
            plt.subplot(2, 2, n)
            plt.ylabel('ou_std')
            plt.yticks(np.linspace(ou_std.min(), ou_std.max(), 5))
        for n in range(4):   # add colorbars to subplots
            plt.subplot(2, 2, n + 1)
            plt.colorbar()
        # Save the figure
        plt.savefig(dirpath_comb / f'result_{pop}.png', dpi=300)


if __name__ == '__main__':
    exp_name = 'batch_i_ougrid_unconn_state1_nosub_wmult_0.1/pv'
    post_batch(exp_name)
