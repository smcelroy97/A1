import json
import os
from pathlib import Path
import pickle
from typing import Tuple, List

import numpy as np
import pandas as pd

import data_proc_utils as proc_utils
import netpyne_res_parse_utils as parse_utils


def create_batch_voltage_table(
        dirpath_exp: str | Path,   # /exp_results/<EXPERIMENT>
        t_limits: Tuple[float, float],   # time limits for rate and CV calculation (in seconds)
        v_ranges: List[Tuple[float, float]]   # voltage ranges to calculate stats
        ) -> None:

    dirpath_exp = Path(dirpath_exp)
    cfg_files = list(dirpath_exp.rglob('*_cfg.json'))
    data_files = [file.with_name(file.stem.replace('_cfg', '_data') + '.pkl')
                for file in cfg_files]

    t_limits = tuple(t * 1000 for t in t_limits)   # seonds -> ms

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

        # Extract voltages by pops.
        V_data, _ = parse_utils.get_voltages(sim_result, t_limits=t_limits)

        # Calculate voltge metrics in the given ranges
        v_metrics = {}
        for pop, V in V_data.items():
            v_metrics[pop] = []
            V_ = V.ravel()   # combine cells
            for v_range in v_ranges:
                vv = V[(V >= v_range[0]) & (V <= v_range[1])]
                v_metrics[pop].append({
                    'num': len(vv),
                    'mean': np.mean(vv),
                    'median': np.median(vv)
                })

        entry = {'ou_mean': ou_mean, 'ou_std': ou_std,
                'v_metrics': v_metrics}
        res.append(entry)

    # Output table columns
    columns = ['ou_mean', 'ou_std']
    pop_names = list(res[0]['v_metrics'].keys())
    for pop in pop_names:
        for v_range in v_ranges:
            for metric in ['num', 'mean', 'median']:
                col_name = f'{pop}_V_{metric}_{v_range[0]}_{v_range[1]}'
                columns.append(col_name)

    # Output table entries
    data = []
    for entry in res:
        row = [entry['ou_mean'], entry['ou_std']]
        for pop in pop_names:
            for k, _ in enumerate(v_ranges):
                for metric in ['num', 'mean', 'median']:
                    row.append(entry['v_metrics'][pop][k][metric])
        data.append(row)

    # Create output DataFrame
    df = pd.DataFrame(data, columns=columns)

    # Save the DataFrame to a CSV file
    fpath_res = dirpath_exp / 'batch_voltages.csv'
    df.to_csv(fpath_res, index=False)


# Example usage
if __name__ == '__main__':
    
    dirpath_exp = Path(
        r'D:\WORK\Salvador\repo\A1_OUinp\exp_results\batch_ougrid_ire_4x4'
    )

    t_limits = (1, 3)   # seconds
    v_ranges = [(-200, 0), (-200, -70), (-70, -50), (-50, 0)]

    create_batch_voltage_table(dirpath_exp, t_limits, v_ranges)