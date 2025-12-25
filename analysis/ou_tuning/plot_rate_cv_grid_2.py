import json
import os
from pathlib import Path
import sys

dirpath_root = Path(__file__).resolve().parents[2]
sys.path.append(str(dirpath_root))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

import xr_utils
from contour_intersect import contour_intersections


# Experiment definition
exp_group = 'batch_i_ougrid_unconn_state1_mech1_nosub_wmult_0.25'
exp_name = 'all'
exp_name_sub = 'exp_ou_nmean_16_nstd_16'

# Values of vmin to choose (ou_mean, ou_std) on the r=r0 contour
vmin0_vals = [-150, -180, -100]


dirpath_self = Path().resolve()
dirpath_cfg_base = dirpath_root / 'exp_configs'
dirpath_res_base = dirpath_root / 'exp_results'

# Load batch result
dirpath_res = (
    dirpath_res_base / exp_group / exp_name / exp_name_sub)
fpath_res = dirpath_res / 'combined' / 'rates_cvs_all.nc'
X = xr.load_dataset(fpath_res)

# Load target firing rates
fpath_target = (
    dirpath_cfg_base / exp_group / exp_name / 'target_state_1.csv')
df = pd.read_csv(fpath_target)
df = df.set_index('pop_name')

# Output folder (for figures)
dirpath_out_fig = dirpath_res / 'ou_sel_figs'
os.makedirs(dirpath_out_fig, exist_ok=True)

vars = ['rate', 'cv', 'v_med_min', 'v_med_max']
ou_pts_sel = {}

for pop in X['pop'].values:
    print(pop)

    # Extract variables, assign (ou_mean, ou_std) coords
    D = {}
    for v in vars:
        X_ = X[v].sel(pop=pop)
        X_ = X_.rename(ou_mean_ind='ou_mean', ou_std_ind='ou_std')
        X_ = X_.assign_coords(
            ou_mean=X['ou_mean'].sel(pop=pop).values,
            ou_std=X['ou_std'].sel(pop=pop).values
        )
        D[v] = X_.T

    # Upsample data
    sz_new = 100
    ou_mean = D['rate'].ou_mean.values
    ou_std = D['rate'].ou_std.values
    ou_mean_new = np.linspace(ou_mean.min(), ou_mean.max(), sz_new)
    ou_std_new = np.linspace(ou_std.min(), ou_std.max(), sz_new)
    for v, X_ in D.items():
        try:
            D[v] = X_.interp(ou_mean=ou_mean_new, ou_std=ou_std_new, method='cubic')
        except:
            D[v] = X_.interp(ou_mean=ou_mean_new, ou_std=ou_std_new, method='linear')

    # Intersection of r=r0 and vmin=vmin0 contours
    r0 = df.loc[pop]['target_rate']
    pts = []
    for vmin0 in vmin0_vals:
        pts_ = contour_intersections(D['rate'], D['v_med_min'], r0, vmin0)
        if not pts_.empty:
            pts.append(pts_)
    pts = pd.concat(pts, ignore_index=True)
    pt = pts.loc[0]
    ou_pts_sel[pop] = {'ou_mean': float(pt['x']), 'ou_std': float(pt['y'])}

    # Plot 2-d maps of r, cv, and v stats
    plt.figure(111, figsize=(10,8))
    plt.clf()
    axes = []
    for n, (v, X_) in enumerate(D.items()):
        ax = plt.subplot(2, 2, n + 1)
        axes.append(ax)
        xr_utils.plot_xr(X_, show_ax_names=True)
        cc = xr_utils.plot_xr_contour(D['rate'], '', [r0], colors=['r'])
        xr_utils.plot_xr_contour(D['cv'], 'cv', [0.5, 1], colors=['k'])
        xr_utils.plot_xr_contour(D['v_med_min'], 'vmin', np.sort(vmin0_vals), colors=['m'])
        plt.title(f'{pop} {v}')
        # Plot the selected point
        plt.plot(pt['x'], pt['y'], 'k.', markersize=10)
    plt.show()

    # Save the figure
    fpath_fig = dirpath_out_fig / f'{pop}.png'
    plt.savefig(fpath_fig, dpi=300)

# Save the selected points
fpath_out = dirpath_res / 'ou_inputs.json'
with open(fpath_out, 'w') as fid:
    json.dump(ou_pts_sel, fid, indent=4)
