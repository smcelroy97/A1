from pathlib import Path


dirpath_self = Path(__file__).resolve().parent


def apply_exp_cfg(cfg):
    
    cfg.duration = 3 * 1e3
    
    # Turn on/off the connections
    cfg.addConn = 0
    
    # OU conductance
    cfg.add_ou_conductance = 1
    cfg.ou_common = 0
    cfg.ou_params_fpath = (dirpath_self / 'ou_inputs.json').as_posix()
