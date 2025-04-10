
def get_batch_params():
    params = {
        'OUamp': [0.002, 0.005, 0.01]
    }    
    return params

def post_update(cfg):    
    cfg.OUstd = cfg.OUamp * 0.4
    
    