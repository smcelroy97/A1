from pathlib import Path

import numpy as np
import pandas as pd


def get_batch_params():
    """Generate params for batchtools to probe. """
    params = {
        'ou_ramp_offset': [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2],
        'bkg_spike_inputs.IT5B.r': [50, 75, 100, 125, 150],
        'bkg_spike_inputs.IT5B.w': [0.1, 0.25, 0.5, 0.75]
    }
    return params


def post_update(cfg):
    """Called after cfg.update() """
    pass


""" if __name__ == '__main__':
    from pprint import pprint
    pop_groups = generate_active_pop_groups()
    for n, name in enumerate(pop_groups):
        print(f'{n} {name}: {" ".join(pop_groups[name])}') """
