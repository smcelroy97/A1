from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
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

def plot_xr_contour(
        Z: xr.DataArray,
        name: str,
        levels: List[float],
        colors: List[str] | None = None,
        style: str = '-',
        xmult: int = 1,
        ymult: int = 1
        ) -> None:

    def fmt_func(x):
        if x == int(x): return f'{name}={int(x)}'
        else: return f'{name}={x:.1f}'
    
    x = Z.coords[Z.dims[1]] * xmult
    y = Z.coords[Z.dims[0]] * ymult

    contours = plt.contour(
        x, y, Z.values, linestyles=style,
        levels=levels, colors=colors
    )
    plt.clabel(contours, inline=True, fontsize=8, 
               fmt=fmt_func, rightside_up=True)

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