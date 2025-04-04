def apply_exp_cfg(cfg):
    
    cfg.duration = 3 * 1e3
    
    # Turn on/off the connections
    cfg.addConn = 1
    
    # OU conductance
    cfg.add_ou_conductance = 1
    cfg.ou_common = 0

