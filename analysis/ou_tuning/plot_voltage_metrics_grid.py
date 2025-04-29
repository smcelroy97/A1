import os
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np

from read_batch_voltages_table import read_batch_voltages_table
from xr_utils import interpolate_to_xr, plot_xr, plot_xr_contour


def plot_voltage_metrics_grid(
        dirpath_exp: str | Path,
        metrics_vis: List[str | Tuple[str, callable]],
        npoints: int = 100,   # grid resolution
        nslices: int = 5,   # num. ou_std==const slices to plot
        show_grid: bool = True,
        dirname_out: str = 'plots_voltage'
        ) -> None:

    # Read and parse batch result table
    fpath_in = dirpath_exp / 'batch_voltages.csv'
    ou_mean, ou_std, data = read_batch_voltages_table(fpath_in)
    data_coords = list(zip(ou_mean, ou_std))
    pop_names = list(data.keys())

    # Properties of the visualized grid
    ou_mean_range = (ou_mean.min(), ou_mean.max())
    ou_std_range = (ou_std.min(), ou_std.max())

    # Interpolate data to fill the visualized grid
    data_interp = {}
    for pop in pop_names:
        data_interp[pop] = {}
        for data_type in metrics_vis:
            
            if isinstance(data_type, tuple):
                # If data_type is a function, apply it to the data
                if not callable(data_type[1]):
                    raise ValueError(f'Expected a callable for {data_type[1]}')
                data_values = data_type[1](data[pop])
                data_type_title = data_type[0]
            else:
                # Otherwise, treat it as a column name
                data_values = data[pop][data_type]
                data_type_title = data_type

            data_interp[pop][data_type] = interpolate_to_xr(
                data_coords,
                data_values,
                ou_mean_range, ou_std_range,
                nx=npoints, ny=npoints,
                coord_names=('ou_mean', 'ou_std')
            )

    # 1D slices of 2D data with ou_std==const
    nslices = 5
    d = (ou_std.max() - ou_std.min()) * 0.1
    ou_std_slices = np.linspace(
        ou_std.min() + d, ou_std.max() - d, nslices)

    # Coordinates multiplier for visualization
    xmult, ymult = 100, 100
    ou_mean *= xmult
    ou_std *= ymult

    margin = 0.05

    nx = 3
    ny = len(metrics_vis)

    def plot_pop_data(pop: str):

        for n, data_type in enumerate(metrics_vis):
            Z = data_interp[pop][data_type]

            if isinstance(data_type, tuple):
                data_type_title = data_type[0]
            else:
                data_type_title = data_type

            # 2D image with rate/CV contours 
            plt.subplot(2, 3, n * nx + 1)
            plot_xr(Z, xmult=xmult, ymult=xmult, margin=margin)
            plt.title(f'{data_type_title}, {pop}')
            if n == ny - 1:
                plt.xlabel(f'ou_mean * {xmult}')
            plt.ylabel(f'ou_std * {ymult}')

            # 2D image with horizontal slicing lines and grid points
            plt.subplot(2, 3, n * nx + 2)
            plot_xr(Z, xmult=xmult, ymult=xmult, margin=margin)
            if show_grid:
                plt.plot(ou_mean, ou_std, 'k.', markersize=1)
            for ou_std_slice in ou_std_slices:
                plt.plot([ou_mean.min(), ou_mean.max()],
                        [ou_std_slice * ymult] * 2,
                        '--', linewidth=2)
            plt.title(f'{data_type_title}, {pop}')
            if n == ny - 1:
                plt.xlabel(f'ou_mean * {xmult}')
            
            # 1D slices: value vs. ou_mean (ou_std==const)
            plt.subplot(2, 3, n * nx + 3)
            for ou_std_slice in ou_std_slices:
                zz = Z.sel(ou_std=ou_std_slice, method='nearest')
                plt.plot(zz.coords['ou_mean'], zz.values)
            #plt.title(f'{data_type_title} slices (ou_std=const), {pop}')
            plt.title(f'Slices (ou_std=const), {pop}')
            if n == ny - 1:
                plt.xlabel(f'ou_mean * {xmult}')
            plt.ylabel(data_type_title)

    # Folder for saving the figures
    dirpath_out = dirpath_exp / dirname_out
    os.makedirs(dirpath_out, exist_ok=True)

    plt.figure(figsize=(14, 7))

    for pop in pop_names:
        print(f'Plotting {pop}...')

        plt.clf()
        plot_pop_data(pop)

        fpath_fig = dirpath_out / f'{pop}.png'
        plt.savefig(fpath_fig, dpi=300)


if __name__ == '__main__':
    # Repo root (two levels above this script)
    dirpath_base = Path(__file__).resolve().parents[2]

    # Experiment config and result folders
    dirpath_exp = dirpath_base / 'exp_results' / 'batch_ougrid_ire_4x4'

    def V_ratio(x):
        return x['V_num_-70_-50']

    metrics_vis = [
        'V_median_-200_0',
        (
            'V_(-50_0)_(-70_-50)_num_ratio',
            lambda x: x['V_num_-50_0'] / x['V_num_-70_-50']
        )
    ]

    plot_voltage_metrics_grid(dirpath_exp, metrics_vis, npoints=100, nslices=5)