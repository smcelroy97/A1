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


def _plot_multi_ramp_r_vs_ou(R, cc, title_postfix=None):
    plt.plot(R.ou_mean,
            R.sel(interval='pre').isel(ou_ramp_offset=0),
            '.', label='pre')
    for n, ramp in enumerate(R.ou_ramp_offset):
        plt.plot(R.ou_mean,
                R.sel(interval='post', ou_ramp_offset=ramp) + 0.5 * (n + 1),
                '.', label=f'post: amp={ramp.item()}')
    plt.xlabel('OU amplitude')
    plt.ylabel('Avg. rate (Hz)')
    title_str = ', '.join([f'{k}={v}' for k, v in cc.items()])
    if title_postfix is not None:
        title_str += ', ' + title_postfix
    plt.title(title_str)
    plt.ylim(-1, 100)
    plt.legend()


def _plot_multi_ramp_v_vs_ou(V, cc, title_postfix=None):
    vv = [(-np.inf, -40), (-40, 0), (0, np.inf)]
    cols = ['r', 'b', 'k']
    
    for _, X in iter_xr_slices_along_dims(V, dims=['cell']):
        vmin = X['vmin'].values
        vmax = X['vmax'].values
        vavg = X['vavg'].values

        for n, vv_ in enumerate(vv):
            mask = (vmax >= vv_[0]) & (vmax < vv_[1])
            ou_mean_ = X.ou_mean.values[mask]
            vmin_ = vmin[mask]
            vmax_ = vmax[mask]
            vavg_ = vavg[mask]
            if n == 2:
                plt.plot(ou_mean_, vmin_, '.', color=cols[n])
                plt.plot(ou_mean_, vmax_, '.', color=cols[n])
            else:
                plt.plot(ou_mean_, vavg_, '.', color=cols[n])

    plt.xlabel('OU mean')
    plt.ylabel('Voltage')

    title_str = ', '.join([f'{k}={v}' for k, v in cc.items()])
    if title_postfix is not None:
        title_str += ', ' + title_postfix
    plt.title(title_str)
    plt.legend()


def post_batch(exp_name):
    dirpath_exp_cfg = dirpath_repo_root / 'exp_configs' / exp_name
    dirpath_exp = dirpath_repo_root / 'exp_results' / exp_name

    #dirpath_exp = dirpath_exp / 'IT2_IT3' / '6_gmult_2_var_ramp_rx_wx'

    # Load var_mechs_info from a JSON file
    with open(dirpath_exp_cfg / 'var_mechs_info.json', 'r') as fid:
        var_mechs_info = json.load(fid)

    # Extract (param_grid -> job_id) xarray from cfg folder
    cfg_param_fields = {
        'ou_ramp_offset': 'ou_ramp_offset',
        'rx': 'bkg_r',
        'wx': 'bkg_w',
        'mech': 'mech_var',
        'mech_mult': 'mech_mult_num'
    }
    job_idx_xr = batch_utils.extract_batch_params_to_xr(
        dirpath_exp / 'cfg',
        cfg_param_fields,
        fname_cfg_templ='cfg_*.json',
        job_pos_in_fname=1
    )

    # Create folder for combined batch results
    dirpath_comb = dirpath_exp / 'combined'
    os.makedirs(dirpath_comb, exist_ok=True)

    # Save job_idx xarray
    job_idx_xr.to_netcdf(dirpath_comb / 'job_idx.nc')

    fmt = {
        'rx': 'rx_{v:03d}',
        'wx': 'wx_{v:.03f}',
        'mech': '{v}'
    }
    def _format(k, v):
        return fmt[k].format(v=v) if k in fmt else f'{k}_{v}'

    #pops = ['IT2', 'IT3']
    #pops = ['IT6', 'CT5A', 'CT5B', 'CT6']
    #pops = ['IT5A', 'ITP4', 'ITS4']
    pops = ['PT5B']

    for pop in pops:

        # Combine rates data from all jobs
        R0 = batch_utils.collect_batch_xr_data(
            job_idx_xr, dirpath_exp / 'rates',
            'rates_' + pop + '_{job:05d}_*.nc'
        )
        R0.to_netcdf(dirpath_comb / f'rates_{pop}_all.nc')

        # Combine voltages data from all jobs
        V0 = batch_utils.collect_batch_xr_data(
            job_idx_xr, dirpath_exp / 'vstats',
            'vstats_' + pop + '_{job:05d}_*.nc'
        )
        V0.to_netcdf(dirpath_comb / f'vstats_{pop}_all.nc')

        # TODO: save job_idx_xr as json

        nx, ny = 2, 2
        
        # Firing rate bifurcation diagram
        slice_dims = ['ou_ramp_offset', 'cell', 'interval', 'mech_mult']
        os.makedirs(dirpath_comb / f'ir_avg_mech_{pop}', exist_ok=True)
        plt.figure(111, figsize=(12, 6))
        for cc, R in iter_xr_slices_along_dims(R0, slice_dims):
            plt.clf()
            for n, _ in enumerate(R.mech_mult):
                plt.subplot(nx, ny, n + 1)
                mult = var_mechs_info[cc['mech']]['mult_vals'][n]
                _plot_multi_ramp_r_vs_ou(R.isel(mech_mult=n), cc,
                                         f'mult={mult}')
            cc_ = {k: cc[k] for k in ['mech', 'rx', 'wx']}
            fname_out = f'ir_avg_{pop}_' + '_'.join(
                [_format(k, v) for k, v in cc_.items()]) + '.png'
            plt.savefig(dirpath_comb / f'ir_avg_mech_{pop}' / fname_out)

        # Voltage bifurcation diagram
        slice_dims = ['ou_ramp_offset', 'cell', 'interval', 'mech_mult']
        os.makedirs(dirpath_comb / f'iv_mech_{pop}', exist_ok=True)
        plt.figure(111, figsize=(12, 6))
        for cc, V in iter_xr_slices_along_dims(V0, slice_dims):
            plt.clf()
            for n, _ in enumerate(V.mech_mult):
                plt.subplot(nx, ny, n + 1)
                mult = var_mechs_info[cc['mech']]['mult_vals'][n]
                _plot_multi_ramp_v_vs_ou(V.isel(mech_mult=n), cc,
                                         f'mult={mult}')
            cc_ = {k: cc[k] for k in ['mech', 'rx', 'wx']}
            fname_out = f'iv_{pop}_' + '_'.join(
                [_format(k, v) for k, v in cc_.items()]) + '.png'
            plt.savefig(dirpath_comb / f'iv_mech_{pop}' / fname_out)


if __name__ == '__main__':
    exp_name = 'batch_i_ou/batch_i_ou_rx_switch_var_oumean_mech_v'
    post_batch(exp_name)
