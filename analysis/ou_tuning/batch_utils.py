import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr


def _extract_nested(x: dict, key_seq: str):
    keys = key_seq.split('.')
    val = x
    for key in keys:
        val = val[key]
    return val

def extract_batch_params_to_xr(
        dirpath_exp: str | Path,
        cfg_param_fields: dict[str, str],
        fname_cfg_templ: str = '*_cfg.json',
        job_pos_in_fname: int = -2,
        ) -> xr.DataArray:
    
    dirpath_exp = Path(dirpath_exp)
    cfg_files = list(dirpath_exp.rglob(fname_cfg_templ))

    #params_by_job_id = {}
    job_idx_by_params = []

    # Read params from cfg files
    for fpath_cfg in cfg_files:
        # Read cfg file
        with open(fpath_cfg) as f:
            cfg = json.load(f)
        
        # Read values of batch params from cfg
        params = {
            par_name: _extract_nested(cfg['simConfig'], field_seq)
            for par_name, field_seq in cfg_param_fields.items()
        }

        # Params -> job ID
        par_lst = [params[par_name] for par_name in cfg_param_fields]
        job_id = int(fpath_cfg.stem.split('_')[job_pos_in_fname])
        job_idx_by_params.append(par_lst + [job_id])
    
    # Build DataFrame
    dims = list(cfg_param_fields.keys())
    job_idx_by_params = pd.DataFrame(
        data=job_idx_by_params,
        columns=dims + ['job_id']
    )

    # Sort coordinates for each dimension
    for dim in dims:
        job_idx_by_params[dim] = pd.Categorical(
            job_idx_by_params[dim],
            categories=sorted(job_idx_by_params[dim].unique()),
            ordered=True
        )

    # Create xarray of job_idx with batch params as dims
    job_idx_xr = job_idx_by_params.set_index(dims).sort_index().to_xarray()['job_id']
    return job_idx_xr


if __name__ == '__main__':

    dirpath_cfg = ('/ddn/niknovikov19/repo/A1_OUinp/exp_results'
               '/batch_i_ou/batch_i_ou_IT5B_rx_switch_var_oumean/cfg')

    cfg_param_fields = {
        'ou_ramp_offset': 'ou_ramp_offset'
    }

    job_idx_xr = extract_batch_params_to_xr(
        dirpath_cfg,
        cfg_param_fields,
        fname_cfg_templ='cfg_*.json',
        job_pos_in_fname=1
    )