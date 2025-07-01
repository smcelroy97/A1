import json
import os
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

dirpath_repo_root = Path(__file__).resolve().parents[3]
sys.path.append(str(dirpath_repo_root))

from analysis.ou_tuning import batch_utils
from analysis.ou_tuning.xr_utils import iter_xr_slices_along_dims


def _plot_multi_ramp_r_vs_ou(R, cc):
    plt.plot(R.ou_mean,
            R.sel(interval='pre').isel(ou_ramp_offset=0),
            '.', label='pre')
    for n, ramp in enumerate(R.ou_ramp_offset[:-3]):
        plt.plot(R.ou_mean,
                R.sel(interval='post', ou_ramp_offset=ramp) + 0.5 * (n + 1),
                '.', label=f'post: amp={ramp.item()}')
    plt.xlabel('OU amplitude')
    plt.ylabel('Avg. rate (Hz)')
    plt.title(', '.join([f'{k}={v}' for k, v in cc.items()]))
    plt.ylim(-1, 70)
    plt.legend()


def post_batch(exp_name):
    dirpath_exp = dirpath_repo_root / 'exp_results' / exp_name

    # Extract (param_grid -> job_id) xarray from cfg folder
    cfg_param_fields = {
        'ou_ramp_offset': 'ou_ramp_offset',
        'rx': 'bkg_spike_inputs.IT5B.r',
        'wx': 'bkg_spike_inputs.IT5B.w'
    }
    job_idx_xr = batch_utils.extract_batch_params_to_xr(
        dirpath_exp / 'cfg',
        cfg_param_fields,
        fname_cfg_templ='cfg_*.json',
        job_pos_in_fname=1
    )

    # Combine job result xarray's into one large xarray
    R0 = batch_utils.collect_batch_xr_data(
        job_idx_xr, dirpath_exp / 'rates', 'rates_{job:05d}_*.nc'
    )
    
    # Create folder for combined batch results
    dirpath_comb = dirpath_exp / 'combined'
    os.makedirs(dirpath_comb, exist_ok=True)
    
    # Save R0 (combined batch data)
    R0.to_netcdf(dirpath_comb / 'rates_all.nc')

    # TODO: save job_idx_xr as json

    fmt = {
        'rx': 'rx_{v:03d}',
        'wx': 'wx_{v:.03f}',
    }
    def _format(k, v):
        return fmt[k].format(v=v) if k in fmt else f'{k}_{v}'

    slice_dims = ['ou_ramp_offset', 'cell', 'interval']
    os.makedirs(dirpath_comb / 'ir_avg', exist_ok=True)
    plt.figure(figsize=(12, 6))
    for cc, R in iter_xr_slices_along_dims(R0, slice_dims):
        plt.clf()
        _plot_multi_ramp_r_vs_ou(R, cc)
        fname_out = 'ir_avg_' + '_'.join(
            [_format(k, v) for k, v in cc.items()]) + '.png'
        plt.savefig(dirpath_comb / 'ir_avg' / fname_out)


if __name__ == '__main__':
    #exp_name = 'batch_i_ou/batch_i_ou_IT5B_rx_switch_var_oumean_mech/2'
    exp_name = 'batch_i_ou/batch_i_ou_IT5B_rx_switch_var_oumean/2'
    post_batch(exp_name)
