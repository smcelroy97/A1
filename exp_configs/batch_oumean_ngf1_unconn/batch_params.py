
def get_batch_params():
    params = {
        'ou_pop_inputs_override.NGF1.ou_mean': [0.003, 0.006, 0.009]
    }    
    return params

def post_update(cfg):    
    cfg.ou_pop_inputs_override['NGF1']['ou_std'] = (
        cfg.ou_pop_inputs_override['NGF1']['ou_mean'] * 0.4
    )