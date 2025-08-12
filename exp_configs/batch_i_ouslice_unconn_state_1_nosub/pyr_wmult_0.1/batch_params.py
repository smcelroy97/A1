from pathlib import Path

import numpy as np
import pandas as pd


dirpath_self = Path(__file__).resolve().parent


# OU batch params
BATCH_PARAMS = {
    'num_ou_points': 10,
    'ou_std_mean_ratio': 0.0,
    'ou_std_intercept': 0.03
}


def get_batch_params():
    """Generate params for batchtools to probe. """
    params = {
        'ou_range_pos': np.linspace(0, 1, BATCH_PARAMS['num_ou_points'])
    }
    return params

def _select_ou_from_range(
        ou_info: pd.DataFrame,
        ou_range_pos: float,
        ou_std_mean_ratio: float,
        ou_std_intercept: float
        ) -> dict[str, dict[str, float]]:
    # Select ou_mean from the range for every pop.
    ou_info['ou_mean'] = (
        ou_info['ou_mean_min'] * (1 - ou_range_pos) +
        ou_info['ou_mean_max'] * ou_range_pos
    )
    # Calculate ou_std from ou_mean
    ou_info['ou_std'] = (
        ou_std_intercept + ou_std_mean_ratio * ou_info['ou_mean']
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
    # Read OU ranges for the pops. from csv file
    ou_info = pd.read_csv(dirpath_self / 'ou_mean_ranges.csv')
    ou_info = ou_info.set_index('pop_name')
    # Select OU from the range for every pop.
    cfg.ou_pop_inputs = _select_ou_from_range(
        ou_info,
        cfg.ou_range_pos,
        BATCH_PARAMS['ou_std_mean_ratio'],
        BATCH_PARAMS['ou_std_intercept']
    )
    # Store batch params into each job's cfg
    #cfg.num_ou_points = BATCH_PARAMS['num_ou_points']
    #cfg.ou_std_mean_ratio = BATCH_PARAMS['ou_std_mean_ratio']
    #cfg.ou_std_intercept = BATCH_PARAMS['ou_std_intercept']

def gen_exp_name_sub():
    """Generate a subfolder name for the results, based on batch params. """
    exp_name_sub = (
        f'exp_npts_{BATCH_PARAMS["num_ou_points"]}_'
        f'std0_{(100 * BATCH_PARAMS["ou_std_intercept"]):.01f}_'
        f'kstd_{(100 * BATCH_PARAMS["ou_std_mean_ratio"]):.01f}'
    )
    return exp_name_sub


if __name__ == '__main__':
    from pprint import pprint
    from netpyne.specs import SimConfig
    cfg = SimConfig()
    cfg.ou_range_pos = 0.25
    post_update(cfg)
