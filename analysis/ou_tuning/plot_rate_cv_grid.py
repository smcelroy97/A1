import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from read_batch_res_table import read_batch_res_table
from xr_utils import interpolate_to_xr, plot_xr, plot_xr_contour


def _get_slice_endpoints(
        ou_mean_vals: np.ndarray,
        ou_std_vals: np.ndarray,
        ou_std_mean_ratio: float,
        ou_std_intercept
        ) -> list[tuple[float, float]]:
    rect_min_x, rect_max_x = ou_mean_vals.min(), ou_mean_vals.max()
    rect_min_y, rect_max_y = ou_std_vals.min(), ou_std_vals.max()

    # Line equation: ou_std = ou_mean * ou_std_mean_ratio + ou_std_intercept
    def line_y(x):
        return x * ou_std_mean_ratio + ou_std_intercept

    def line_x(y):
        return (y - ou_std_intercept) / ou_std_mean_ratio

    # Calculate intersections
    intersections = []

    # Check intersection with left edge (x = rect_min_x)
    y = line_y(rect_min_x)
    if rect_min_y <= y <= rect_max_y:
        intersections.append((rect_min_x, y))

    # Check intersection with right edge (x = rect_max_x)
    y = line_y(rect_max_x)
    if rect_min_y <= y <= rect_max_y:
        intersections.append((rect_max_x, y))

    # Check intersection with bottom edge (y = rect_min_y)
    x = line_x(rect_min_y)
    if rect_min_x <= x <= rect_max_x:
        intersections.append((x, rect_min_y))

    # Check intersection with top edge (y = rect_max_y)
    x = line_x(rect_max_y)
    if rect_min_x <= x <= rect_max_x:
        intersections.append((x, rect_max_y))

    # Return the pair of intersection points
    return intersections[:2]

def _generate_slices(
        ou_mean_vals: np.ndarray,
        ou_std_vals: np.ndarray,
        nslices: int | None = None,     # num. ou_std==const slices to plot
        slice_d: float | None = None,   # relative margin between 1-st slice and min. ou_std
        slices: list[tuple[float, float]] | None = None  # list of (std_mean_ratio, std_intercept) tuples
        ) -> list[list[tuple[float, float]]]:   # list of point pairs
    if slices is not None:
        return [_get_slice_endpoints(ou_mean_vals, ou_std_vals, *slice)
                for slice in slices]
    else:
        d = (ou_std_vals.max() - ou_std_vals.min()) * slice_d
        ou_std_slices = np.linspace(
            ou_std_vals.min() + d, ou_std_vals.max() - d, nslices)
        return [[(ou_mean_vals.min(), ou_std_slice), (ou_mean_vals.max(), ou_std_slice)]
                for ou_std_slice in ou_std_slices]

def _get_xr_slice(
        Z: xr.DataArray,   # xarray with dims (ou_mean, ou_std)
        slice_pt1: tuple[float, float],  # (ou_mean, ou_std)
        slice_pt2: tuple[float, float],  # (ou_mean, ou_std)
        num_points: int = 100
        ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Get a 1D slice of the 2D xarray along the line between two points."""
    x1, y1 = slice_pt1
    x2, y2 = slice_pt2
    x_vals = np.linspace(x1, x2, num_points)
    y_vals = np.linspace(y1, y2, num_points)
    slice_values = Z.interp(ou_mean=xr.DataArray(x_vals, dims="points"),
                            ou_std=xr.DataArray(y_vals, dims="points"),
                            method="linear").values
    return x_vals, y_vals, slice_values

def plot_rate_cv_grid(
        dirpath_exp: str | Path,
        npoints: int = 100,   # grid resolution
        nslices: int = 5,   # num. ou_std==const slices to plot
        slice_d: float = 0.1,   # relative margin between 1-st slice and min. ou_std
        show_grid: bool = True,
        show_r_cv_contours: bool = False,
        dirname_out: str = 'plots',
        slices: list[tuple[float, float]] | None = None  # list of (std_mean_ratio, std_intercept) tuples
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

    # 1D slices of 2D data
    slice_pts = _generate_slices(
        ou_mean, ou_std,
        nslices=nslices, slice_d=slice_d, slices=slices
    )

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
            for slice_endpoints in slice_pts:
                (x1, y1), (x2, y2) = slice_endpoints
                plt.plot([x1 * xmult, x2 * xmult],
                         [y1 * ymult, y2 * ymult],
                         '--', linewidth=2)
            plt.title(f'{data_type}, {pop}')
            if n == ny - 1:
                plt.xlabel(f'ou_mean * {xmult}')
            
            # 1D slices: value vs. ou_mean (ou_std==const)
            plt.subplot(2, 3, n * nx + 3)
            for slice_endpoints in slice_pts:
                ou_mean_, _, slice_values = _get_xr_slice(Z, *slice_endpoints, num_points=npoints)
                plt.plot(ou_mean_ * xmult, slice_values, '-', linewidth=2)
            plt.title(f'{data_type} slices, {pop}')
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