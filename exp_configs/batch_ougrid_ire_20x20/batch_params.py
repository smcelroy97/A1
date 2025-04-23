from pathlib import Path
import pandas as pd


def get_batch_params():
    """Generate params for batchtools to probe. """
    
    # Read a list of (ou_mean, ou_std) tuples from a CSV file
    fpath_ou_grid = Path(__file__).resolve().parent / 'ou_grid.csv'
    df = pd.read_csv(fpath_ou_grid)
    ou_tuples = list(df.itertuples(index=False, name=None))

    # Put the list of tuples to batch params
    params = {
        'ou_tuple': ou_tuples  # (OUamp, OUstd)
    }
    return params


def post_update(cfg):
    """Called after cfg.update() """
        
    cfg.OUamp = cfg.ou_tuple[0]
    cfg.OUstd = cfg.ou_tuple[1]


if __name__ == '__main__':
    from pprint import pprint
    par = get_batch_params()
    pprint(par)