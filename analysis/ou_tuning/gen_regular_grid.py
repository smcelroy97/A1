from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


def gen_regular_grid(
        ou_mean_range: Tuple[float, float],
        ou_mean_npoints: int,
        ou_std_range: Tuple[float, float],
        ou_std_npoints: int,
        fpath_out: str | Path,
        need_save: True
        ) -> None:
    """Generate a regular grid of OU mean and std values. """
    # Generate grid
    ou_mean_values = np.linspace(
        ou_mean_range[0], ou_mean_range[1], ou_mean_npoints
    )
    ou_std_values = np.linspace(
        ou_std_range[0], ou_std_range[1], ou_std_npoints
    )
    grid = np.array(np.meshgrid(ou_mean_values, ou_std_values)).T.reshape(-1, 2)
    
    # Save grid to CSV
    if need_save:
        df = pd.DataFrame(grid, columns=["ou_mean", "ou_std"])
        df.to_csv(fpath_out, index=False)

    else:
        return grid


if __name__ == '__main__':
    
    # Define the ranges and number of points for the grid
    ou_mean_range = (-0.06, 0.05)
    ou_mean_npoints = 4
    ou_std_range = (0, 0.05)
    ou_std_npoints = 4

    # Experiment name
    exp_name = 'batch_ougrid_itp4_4x4_med_3s'

    # Define the output file path
    fpath_out = (
        Path(__file__).resolve().parents[2] /  # two levels above this script
        'exp_configs' / exp_name / 'ou_grid.csv'
    )

    # Generate and save the grid
    need_save = True
    if fpath_out.exists():
        user_input = input(f"{fpath_out} already exists. Replace it? (y/n): ").strip().lower()
        if user_input != 'y':
            print("Operation cancelled.")
            need_save = False
    if need_save:
        gen_regular_grid(ou_mean_range, ou_mean_npoints,
                         ou_std_range, ou_std_npoints,
                         fpath_out)