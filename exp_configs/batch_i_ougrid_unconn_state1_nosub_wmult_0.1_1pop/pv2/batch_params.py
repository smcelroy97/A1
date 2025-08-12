from pathlib import Path

import numpy as np
import pandas as pd


dirpath_self = Path(__file__).resolve().parent


# OU batch params
BATCH_PARAMS = {
    'num_ou_mean_points': 10,
    'num_ou_std_points': 10,
    'ou_range': {
        'PV2': {
            'ou_mean': (-0.06, 0.03),
            'ou_std': (0, 0.04)
        }
    }
}

def get_batch_params():
    """Generate params for batchtools to probe. """
    params = {
        'ou_mean_pos': np.linspace(0, 1, BATCH_PARAMS['num_ou_mean_points']),
        'ou_std_pos': np.linspace(0, 1, BATCH_PARAMS['num_ou_std_points'])
    }
    return params

def _select_ou_from_range(
        ou_mean_pos: float,
        ou_std_pos: float
        ) -> dict[str, dict[str, float]]:
    # Select ou_mean and ou_std from the range for every pop.
    ou_pop_inputs = {}
    for pop, range in BATCH_PARAMS['ou_range'].items():
        ou_mean = (
            range['ou_mean'][0] * (1 - ou_mean_pos) +
            range['ou_mean'][1] * ou_mean_pos
        )
        ou_std = (
            range['ou_std'][0] * (1 - ou_std_pos) +
            range['ou_std'][1] * ou_std_pos
        )
        ou_pop_inputs[pop] = {'ou_mean': ou_mean, 'ou_std': ou_std}
    return ou_pop_inputs

def post_update(cfg):
    """Called after cfg.update() """
    # Select OU from the range for every pop.
    cfg.ou_pop_inputs = _select_ou_from_range(
        cfg.ou_mean_pos, cfg.ou_std_pos
    )

def gen_exp_name_sub():
    """Generate a subfolder name for the results, based on batch params. """
    pop = next(iter(BATCH_PARAMS['ou_range']))
    ou_mean_range = np.array(BATCH_PARAMS['ou_range'][pop]['ou_mean']) * 100
    ou_std_range = np.array(BATCH_PARAMS['ou_range'][pop]['ou_std']) * 100
    npts_mean = BATCH_PARAMS['num_ou_mean_points']
    npts_std = BATCH_PARAMS['num_ou_std_points']
    exp_name_sub = (
        'exp_'
        f'oumean_{ou_mean_range[0]:.01f}_{ou_mean_range[1]:.01f}_{npts_mean}_'
        f'oustd_{ou_std_range[0]:.01f}_{ou_std_range[1]:.01f}_{npts_std}'
    )
    return exp_name_sub


if __name__ == '__main__':
    from pprint import pprint
    from netpyne.specs import SimConfig
    cfg = SimConfig()
    cfg.ou_range_pos = 0.25
    post_update(cfg)
