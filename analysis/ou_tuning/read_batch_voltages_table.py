import os
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd


def read_batch_voltages_table(
        fpath_in: str | Path
        ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Dict[str, np.ndarray]]]:
    # Returns: ou_mean, ou_std, {pop: {metric: values}}

    # Read the CSV file into a pandas DataFrame
    fpath_in = Path(fpath_in)
    df = pd.read_csv(fpath_in)

    # Create a list of (ou_mean, ou_std) tuples
    ou_mean = df['ou_mean'].to_numpy()
    ou_std = df['ou_std'].to_numpy()

    # Extract pop_names
    pop_names = list({col.split('_')[0] for col in df.columns if col not in {'ou_mean', 'ou_std'}})

    # Read pop rates and Cv's from df
    data = {}
    for pop in pop_names:
        metrics = [col[len(pop) + 1:] for col in df.columns if col.startswith(f'{pop}_')]
        data[pop] = {metric: df[f'{pop}_{metric}'].to_numpy() for metric in metrics}
    
    return ou_mean, ou_std, data


if __name__ == '__main__':

    dirpath_exp = Path(
        r'D:\WORK\Salvador\repo\A1_OUinp\exp_results\batch_ougrid_ire_4x4'
    )
    fpath_in = dirpath_exp / 'batch_voltages.csv'

    ou_mean, ou_std, data = read_batch_voltages_table(fpath_in)

    from pprint import pprint
    pprint(data)