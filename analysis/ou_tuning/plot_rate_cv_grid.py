import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from read_batch_res_table import read_batch_res_table
from xr_utils import interpolate_to_xr, plot_xr, plot_xr_contour


def plot_rate_cv_grid(
        dirpath_exp: str | Path,
        npoints: int = 100,   # grid resolution
        nslices: int = 5,   # num. ou_std==const slices to plot
        slice_d: float = 0.1,   # relative margin between 1-st slice and min. ou_std
        show_grid: bool = True,
        show_r_cv_contours: bool = False,
        dirname_out: str = 'plots'
        ) -> None:

    # Read and parse batch result table
    fpath_in = dirpath_exp / 'batch_result.csv'
    ou_mean, ou_std, data = read_batch_res_table(fpath_in)
    data_coords = list(zip(ou_mean, ou_std))
    pop_names = list(data.keys())

    # Properties of the visualized grid
    ou_mean_range = (ou_mean.min(), ou_mean.max())
    ou_std_range = (ou_std.min(), ou_std.max())

    # Interpolate data to fill the visualized grid
    data_interp = {}
    for pop in pop_names:
        data_interp[pop] = {}
        for data_type in ('Rate', 'CV'):
            data_interp[pop][data_type] = interpolate_to_xr(
                data_coords,
                data[pop][data_type],
                ou_mean_range, ou_std_range,
                nx=npoints, ny=npoints,
                coord_names=('ou_mean', 'ou_std')
            )

    # 1D slices of 2D data with ou_std==const
    d = (ou_std.max() - ou_std.min()) * slice_d
    ou_std_slices = np.linspace(
        ou_std.min() + d, ou_std.max() - d, nslices)

    # Coordinates multiplier for visualization
    xmult, ymult = 100, 100
    ou_mean *= xmult
    ou_std *= ymult

    margin = 0.05

    nx = 3
    ny = 2

    def plot_pop_data(pop: str):

        for n, data_type in enumerate(['Rate', 'CV']):
            Z = data_interp[pop][data_type]

            # 2D image with rate/CV contours 
            plt.subplot(2, 3, n * nx + 1)
            plot_xr(Z, xmult=xmult, ymult=xmult, margin=margin)
            if show_r_cv_contours:
                plot_xr_contour(
                    data_interp[pop]['Rate'], 'r', levels=[5, 10],
                    colors=['r', 'k'], style='-',
                    xmult=xmult, ymult=xmult
                )
                plot_xr_contour(
                    data_interp[pop]['CV'], 'CV', levels=[0.5, 1],
                    colors=['r', 'k'], style='--',
                    xmult=xmult, ymult=xmult
                )
            plt.title(f'{data_type}, {pop}')
            if n == ny - 1:
                plt.xlabel(f'ou_mean * {xmult}')
            plt.ylabel(f'ou_std * {ymult}')

            # 2D image with horiontal slicing lines and grid points
            plt.subplot(2, 3, n * nx + 2)
            plot_xr(Z, xmult=xmult, ymult=xmult, margin=margin)
            if show_grid:
                plt.plot(ou_mean, ou_std, 'k.', markersize=1)
            for ou_std_slice in ou_std_slices:
                plt.plot([ou_mean.min(), ou_mean.max()],
                        [ou_std_slice * ymult] * 2,
                        '--', linewidth=2)
            plt.title(f'{data_type}, {pop}')
            if n == ny - 1:
                plt.xlabel(f'ou_mean * {xmult}')
            
            # 1D slices: value vs. ou_mean (ou_std==const)
            plt.subplot(2, 3, n * nx + 3)
            for ou_std_slice in ou_std_slices:
                zz = Z.sel(ou_std=ou_std_slice, method='nearest')
                plt.plot(zz.coords['ou_mean'], zz.values)
            plt.title(f'{data_type} slices (ou_std=const), {pop}')
            if n == ny - 1:
                plt.xlabel(f'ou_mean * {xmult}')
            plt.ylabel(data_type)

    # Folder for saving the figures
    dirpath_out = dirpath_exp / dirname_out
    os.makedirs(dirpath_out, exist_ok=True)

    #plt.ion()
    plt.figure(figsize=(14, 7))

    for pop in pop_names:
        print(f'Plotting {pop}...')

        plt.clf()
        plot_pop_data(pop)

        fpath_fig = dirpath_out / f'{pop}.png'
        plt.savefig(fpath_fig, dpi=300)

    #plt.show()
    #input('Press any key...')


if __name__ == '__main__':

    # Repo root (two levels above this script)
    dirpath_base = Path(__file__).resolve().parents[2]

    # Experiment name
    exp_name = 'batch_ougrid_ire_4x4'
    dirpath_exp = dirpath_base / 'exp_results' / exp_name

    plot_rate_cv_grid(dirpath_exp, npoints=100, nslices=5,
                      show_r_cv_contours=True)