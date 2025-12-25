"""
This script reads a batch simulation result folder,
extracts the OU parameters from the json config files,
calculates the firing rates and CVs from pkl files,
and saves the result as an xarray.

"""

import argparse
import json
import os
from pathlib import Path
import pickle

import numpy as np
import xarray as xr

import data_proc_utils as proc_utils
import netpyne_res_parse_utils as parse_utils


def batch_res_to_xr(
        dirpath_exp: str | Path,   # /exp_results/<EXPERIMENT>
        t_limits: tuple[float, float],   # time limits for rate and CV calculation
        nspikes_min: int,   # min. number of spikes to use a cell in CV calcualtion
        pops_used: list[str] | None = None
        ) -> None:

    # Enumerate jobs
    dirpath_exp = Path(dirpath_exp)
    cfg_files = list(dirpath_exp.rglob('*_cfg.json'))
    data_files = [file.with_name(file.stem.replace('_cfg', '_data') + '.pkl')
                  for file in cfg_files]
    
    # Get pop. names
    with open(cfg_files[0], 'r') as fid:
        cfg = json.load(fid)['simConfig']
    pop_names = list(cfg['ou_pop_inputs'])
    if pops_used is not None:
        pop_names = [pop for pop in pop_names if pop in pops_used]

    # Allocate data buffer
    npops = len(pop_names)
    njobs = len(cfg_files)
    Z = xr.DataArray(
        np.full((npops, njobs), np.nan),
        dims=['pop', 'job'],
        coords={'pop': pop_names, 'job': np.arange(njobs)}
    )
    z = xr.DataArray(
        np.full(njobs, np.nan),
        dims=['job'],
        coords={'job': np.arange(njobs)}
    )
    X = {}
    for var in ['ou_mean', 'ou_std', 'rate', 'cv']:
        X[var] = Z.copy()
    for var in ['ou_range_pos']:
        X[var] = z.copy()
    X = xr.Dataset(X)

    # Attributes
    X.attrs['dirpath_exp'] = str(dirpath_exp)
    X.attrs['t_limits'] = t_limits
    X.attrs['nspikes_min'] = nspikes_min

    for n, (cfg_file, data_file) in enumerate(zip(cfg_files, data_files)):
        # Get job id
        job_id = int(cfg_file.stem[-9:-4])
        print(f'Job: {job_id:05d}', flush=True)

        # Load config
        with open(cfg_file, 'r') as fid:
            cfg = json.load(fid)['simConfig']

        # Load sim result
        with open(data_file, 'rb') as fid:
            sim_result = pickle.load(fid)

        # Calculate firing rates
        spikes = parse_utils.get_net_spikes(sim_result, pop_names=pop_names)
        ncells = parse_utils.get_net_size(sim_result)
        rates = proc_utils.calc_net_rates(spikes, time_limits=t_limits,
                                          ncells=ncells)

        # Calculate CVs
        cell_spikes = parse_utils.get_net_spikes(sim_result,
                                                 combine_cells=False)
        cvs = proc_utils.calc_net_cvs(cell_spikes, time_limits=t_limits,
                                      nspikes_min=nspikes_min, avg_result=True)
        
        for pop in pop_names:
            cc = {'pop': pop, 'job': job_id}
            X['ou_mean'].loc[cc] = cfg['ou_pop_inputs'][pop]['ou_mean']
            X['ou_std'].loc[cc] = cfg['ou_pop_inputs'][pop]['ou_std']
            X['rate'].loc[cc] = rates[pop]
            X['cv'].loc[cc] = cvs[pop]

        X['ou_range_pos'].loc[{'job': job_id}] = cfg['ou_range_pos']

    # Save the xarray
    fpath_res = dirpath_exp / 'analysis' / 'batch_result.nc'
    os.makedirs(fpath_res.parent, exist_ok=True)
    X.to_netcdf(fpath_res)


if __name__ == '__main__':
    #dirpath_exp = '/ddn/niknovikov19/repo/A1_OUinp/exp_results/batch_g_ou_subnet_wmult_0.02_som4_ire_2'
    #batch_res_to_xr(dirpath_exp, t_limits=(2, 3), nspikes_min=3, pops_used=['SOM4', 'IRE'])

    parser = argparse.ArgumentParser(description="Process batch simulation results into an xarray.")
    parser.add_argument("exp_name", type=str, help="Experiment name.")
    parser.add_argument("--t_limits", type=float, nargs=2, default=(2.0, 3.0),
                        help="Time limits for rate and CV calculation (default: (2.0, 3.0)).")
    parser.add_argument("--nspikes_min", type=int, default=3,
                        help="Minimum number of spikes to use a cell in CV calculation (default: 3).")
    parser.add_argument("--pops", type=str, default=None,
                        help="Populations to include (default: None).")
    args = parser.parse_args()
    
    dirpath_exp = Path(__file__).resolve().parents[2] / 'exp_results' / args.exp_name
    pops_used = args.pops.split(' ') if args.pops else None

    batch_res_to_xr(dirpath_exp,
                    t_limits=tuple(args.t_limits),
                    nspikes_min=args.nspikes_min,
                    pops_used=pops_used)
