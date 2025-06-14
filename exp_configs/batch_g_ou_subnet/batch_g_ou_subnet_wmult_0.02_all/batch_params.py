from pathlib import Path

import numpy as np
import pandas as pd


dirpath_self = Path(__file__).resolve().parent

def get_batch_params():
    """Generate params for batchtools to probe. """
    params = {
        'ou_range_pos': np.linspace(0, 1, 8)
    }
    return params


def post_update(cfg):
    """Called after cfg.update() """

    ou_std_mean_ratio = 0.4
    ou_std_intercept = 0.005
        
    ou_info = pd.read_csv(dirpath_self / 'ou_mean_ranges.csv')
    ou_info = ou_info.set_index('pop_name')
    ou_info['ou_mean'] = (
        ou_info['ou_mean_min'] * (1 - cfg.ou_range_pos) +
        ou_info['ou_mean_max'] * cfg.ou_range_pos
    )
    ou_info['ou_std'] = (
        ou_std_intercept + ou_std_mean_ratio * ou_info['ou_mean']
    )

    cfg.ou_pop_inputs = {}
    for pop in ou_info.index:
        print(f'Pop: {pop}', flush=True)
        print(f"Mean: {ou_info.at[pop, 'ou_mean']}", flush=True)
        print(f"Std: {ou_info.at[pop, 'ou_std']}", flush=True)
        cfg.ou_pop_inputs[pop] = {
            'ou_mean': float(ou_info.at[pop, 'ou_mean']),
            'ou_std': float(ou_info.at[pop, 'ou_std']),
        }


if __name__ == '__main__':
    from pprint import pprint
    from netpyne.specs import SimConfig
    cfg = SimConfig()
    cfg.ou_range_pos = 0.25
    post_update(cfg)
