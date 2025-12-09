#import numpy as np


def get_batch_params():
    """Generate params for batchtools to probe. """
    params = {
        'pulse_freq': [2, 3, 4, 5]
    }
    return params


def post_update(cfg):
    """Called after cfg.update() """

    T = 1000 / cfg.pulse_freq
    n_pulses = int(cfg.duration / T)
    r = cfg.pulse_seq_params['rates']

    cfg.pulse_seq_params['period'] = T
    cfg.pulse_seq_params['n_pulses'] = n_pulses
    cfg.pulse_seq_params['rates'] = [r] * n_pulses
