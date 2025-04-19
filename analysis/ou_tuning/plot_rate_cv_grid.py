import os
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
import xarray as xr


def plot_xr(Z: xr.DataArray, vmin=None, vmax=None,
            show_ax_names=False, colorbar=True,
            xmult=1, ymult=1, margin=0):
    """Plot 2D xarray. """

    xx = Z.coords[Z.dims[1]] * xmult
    yy = Z.coords[Z.dims[0]] * ymult
    xmin, xmax, ymin, ymax = xx.min(), xx.max(), yy.min(), yy.max()

    extent = (xmin, xmax, ymin, ymax)
    plt.imshow(Z, origin='lower', aspect='auto', extent=extent,
               vmin=vmin, vmax=vmax)
    
    xmargin = (xmax - xmin) * margin
    ymargin = (ymax - ymin) * margin
    plt.xlim(xmin - xmargin, xmax + xmargin)
    plt.ylim(ymin - ymargin, ymax + ymargin)
    
    if show_ax_names:
        plt.xlabel(f'{Z.dims[1]} * {xmult}')
        plt.ylabel(f'{Z.dims[0]} * {ymult}')
    
    if colorbar:
        plt.colorbar()

def interpolate_to_xr(
        data_coords: List[Tuple[float, float]],  # (x, y),
        data_values: np.ndarray,
        xrange: Tuple[float, float], 
        yrange: Tuple[float, float],
        nx: int = 50,
        ny: int = 50,
        coord_names: Tuple[str, str] = ('x', 'y'),
        method: str = 'cubic'
        ) -> xr.DataArray:
    """Create 2D xarray by interpolating a list of data points. """

    data_coords = np.array(data_coords)
    mask = ~np.isnan(data_values)
    data_values = data_values[mask]
    xx_in = [c[0] for c in data_coords[mask]]
    yy_in = [c[1] for c in data_coords[mask]]

    xx_out = np.linspace(xrange[0], xrange[1], nx)
    yy_out = np.linspace(yrange[0], yrange[1], ny)
    y_grid, x_grid = np.meshgrid(yy_out, xx_out, indexing='ij')
    
    values_interp = griddata(
        (yy_in, xx_in),        # known coordinates
        data_values,           # known values
        (y_grid, x_grid),      # target grid
        method=method
    )
    return xr.DataArray(
        values_interp,
        dims=(coord_names[1], coord_names[0]),
        coords=[(coord_names[1], yy_out),
                (coord_names[0], xx_out)]
    )


exp_name = 'its4_10x10_large'

dirpath_root = Path(__file__).resolve().parents[2]   # two levels above this script
fpath_in = dirpath_root / 'exp_results' / exp_name / 'batch_result.csv'

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(fpath_in)

# Create a list of (ou_mean, ou_std) tuples
ou_mean = df['ou_mean'].to_numpy()
ou_std = df['ou_std'].to_numpy()
data_coords = list(zip(ou_mean, ou_std))

# Extract pop_names
rate_columns = [col for col in df.columns if col.endswith('_r')]
pop_names = [col[:-2] for col in rate_columns]

# Read pop rates and Cv's from df
data = {}
for pop in pop_names:
    data[pop] = {
        'Rate': df[f'{pop}_r'].to_numpy(),
        'CV': df[f'{pop}_cv'].to_numpy()
    }

# Properties of the visualized grid
ou_mean_range = (ou_mean.min(), ou_mean.max())
ou_std_range = (ou_std.min(), ou_std.max())
npoints = 100

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
ny = 2

def plot_pop_data(pop: str):

    for n, data_type in enumerate(['Rate', 'CV']):
        Z = data_interp[pop][data_type]

        # 2D image with grid points marked
        plt.subplot(2, 3, n * nx + 1)
        plot_xr(Z, xmult=xmult, ymult=xmult, margin=margin)
        plt.plot(ou_mean, ou_std, 'k.')
        plt.title(f'{data_type}, {pop}')
        if n == ny - 1:
            plt.xlabel(f'ou_mean * {xmult}')
        plt.ylabel(f'ou_std * {ymult}')

        # 2D image with horiontal slicing lines
        plt.subplot(2, 3, n * nx + 2)
        plot_xr(Z, xmult=xmult, ymult=xmult, margin=margin)
        for ou_std_slice in ou_std_slices:
            plt.plot([ou_mean.min(), ou_mean.max()],
                    [ou_std_slice * ymult] * 2,
                    '--')
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
dirpath_out = dirpath_root / 'exp_results' / exp_name / 'plots'
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