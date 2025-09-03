from pathlib import Path

import numpy as np
import pandas as pd


dirpath_self = Path(__file__).resolve().parent


# OU batch params
BATCH_PARAMS = {
    'num_ou_mean_points': 10,
    'num_ou_std_points': 10,
}

def get_batch_params():
    """Generate params for batchtools to probe. """
    params = {
        'ou_mean_pos': np.linspace(0, 1, BATCH_PARAMS['num_ou_mean_points']),
        'ou_std_pos': np.linspace(0, 1, BATCH_PARAMS['num_ou_std_points'])
    }
    return params

def select_ou_from_range(
        ou_mean_pos: float,
        ou_std_pos: float
        ) -> dict[str, dict[str, float]]:
    # Read OU ranges for the pops. from csv file
    ou_info = pd.read_csv(dirpath_self / 'ou_ranges.csv')
    ou_info = ou_info.set_index('pop_name')
    # Select ou_mean and ou_std from the ranges for every pop.
    ou_info['ou_mean'] = (
        ou_info['ou_mean_min'] * (1 - ou_mean_pos) +
        ou_info['ou_mean_max'] * ou_mean_pos
    )
    ou_info['ou_std'] = (
        ou_info['ou_std_min'] * (1 - ou_std_pos) +
        ou_info['ou_std_max'] * ou_std_pos
    )
    # Convert the result to a dict
    ou_pop_inputs = {}
    for pop in ou_info.index:
        ou_pop_inputs[pop] = {
            'ou_mean': float(ou_info.at[pop, 'ou_mean']),
            'ou_std': float(ou_info.at[pop, 'ou_std']),
        }
    return ou_pop_inputs

def post_update(cfg):
    """Called after cfg.update() """
    # Select OU from the range for every pop.
    cfg.ou_pop_inputs = select_ou_from_range(
        cfg.ou_mean_pos, cfg.ou_std_pos)

def gen_exp_name_sub():
    """Generate a subfolder name for the results, based on batch params. """
    npts_mean = BATCH_PARAMS['num_ou_mean_points']
    npts_std = BATCH_PARAMS['num_ou_std_points']
    exp_name_sub = f'exp_ou_nmean_{npts_mean}_nstd_{npts_std}'
    return exp_name_sub


if __name__ == '__main__':
    from pprint import pprint
    from netpyne.specs import SimConfig
    cfg = SimConfig()
    cfg.ou_range_pos = 0.25
    post_update(cfg)
