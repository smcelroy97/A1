from pathlib import Path

import numpy as np
import pandas as pd


dirpath_self = Path(__file__).resolve().parent


# OU batch params
BATCH_PARAMS = {
    'pop_name': 'PT5B',
    'ou_mean_range': (-0.05, 0.1),
    'ou_std': 0,
    'num_ou_points': 20,
    'tcalc_min': 5
}


def get_batch_params():
    """Generate params for batchtools to probe. """
    params = {
        'ou_mean': np.linspace(
            BATCH_PARAMS['ou_mean_range'][0],
            BATCH_PARAMS['ou_mean_range'][1],
            BATCH_PARAMS['num_ou_points']
        )
    }
    return params

def post_update(cfg):
    """Called after cfg.update() """
    # Set OU mean and std
    pop = BATCH_PARAMS['pop_name']
    cfg.ou_pop_inputs[pop] = {}
    cfg.ou_pop_inputs[pop]['ou_mean'] = cfg.ou_mean
    cfg.ou_pop_inputs[pop]['ou_std'] = BATCH_PARAMS['ou_std']
    # Store batch params into each job's cfg
    cfg.num_ou_points = BATCH_PARAMS['num_ou_points']
    cfg.ou_mean_range = BATCH_PARAMS['ou_mean_range']
    cfg.ou_std = BATCH_PARAMS['ou_std']
