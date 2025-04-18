from pathlib import Path
import pandas as pd
import sys

dirpath_base = Path(__file__).resolve().parents[2]
sys.path.append(str(dirpath_base))
from filter_old_jobs import filter_old_jobs


def get_batch_params():
    """Generate params for batchtools to probe. """

    # Read a list of (ou_mean, ou_std) tuples from a CSV file
    dirpath_self = Path(__file__).resolve().parent
    fpath_ou_grid = dirpath_self / 'ou_grid.csv'
    df = pd.read_csv(fpath_ou_grid)

    skip_finished_jobs = True

    # Remove previously completed jobs from df
    if skip_finished_jobs:
        exp_name = dirpath_self.name
        dirpath_res = dirpath_self.parents[1] / 'exp_results' / exp_name
        df = filter_old_jobs(dirpath_res, df)

    # Put the list of tuples to batch params
    ou_tuples = list(df.itertuples(index=False, name=None))
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
