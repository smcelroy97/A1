""" from pathlib import Path
import pickle

import netpyne_res_parse_utils as utils


fpath_in = (
    '/ddn/niknovikov19/repo/A1_OUinp/exp_results/batch_i_ou'
    '/batch_i_ou_rx_switch_var_oumean_mech_v/batch_i_ou_rx_switch_var_oumean_mech_v_00000_data.pkl'
)
with open(fpath_in, 'rb') as fid:
    X = pickle.load(fid)

V, t = utils.get_voltages(X) """


import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from xr_utils import iter_xr_slices_along_dims

fpath_in = (
    '/ddn/niknovikov19/repo/A1_OUinp/exp_results/batch_i_ou'
    '/batch_i_ou_rx_switch_var_oumean_mech_v/combined/vstats_IT2_all.nc'
)
V0 = xr.open_dataset(fpath_in)

def _plot_multi_ramp_v_vs_ou(V, cc, title_postfix=None):
    
    vv = [(-np.inf, -40), (-40, 0), (0, np.inf)]
    cols = ['r', 'b', 'k']
    
    for _, X in iter_xr_slices_along_dims(V, dims=['cell']):
        vmin = X['vmin'].values
        vmax = X['vmax'].values
        vavg = X['vavg'].values

        for n, vv_ in enumerate(vv):
            mask = (vmax >= vv_[0]) & (vmax < vv_[1])
            ou_mean_ = X.ou_mean.values[mask]
            vmin_ = vmin[mask]
            vmax_ = vmax[mask]
            vavg_ = vavg[mask]
            if n == 2:
                plt.plot(ou_mean_, vmin_, '.', color=cols[n])
                plt.plot(ou_mean_, vmax_, '.', color=cols[n])
            else:
                plt.plot(ou_mean_, vavg_, '.', color=cols[n])

    plt.xlabel('OU mean')
    plt.ylabel('Voltage')
    
    title_str = ', '.join([f'{k}={v}' for k, v in cc.items()])
    if title_postfix is not None:
        title_str += ', ' + title_postfix
    plt.title(title_str)
    plt.legend()

var_mechs_info = {
    'gkdr_all': {'sec': 'all', 'mech': 'kdr', 'par': 'gbar',
                 'mult_vals': [1, 2, 3, 4]}
}

pop = 'IT2'

slice_dims = ['ou_ramp_offset', 'cell', 'interval', 'mech_mult']
plt.figure(111)
for cc, V in iter_xr_slices_along_dims(V0, slice_dims):
    plt.clf()
    for n, _ in enumerate(V.mech_mult):
        #plt.subplot(2, 2, n + 1)
        mult = var_mechs_info[cc['mech']]['mult_vals'][n]
        _plot_multi_ramp_v_vs_ou(V.sel(mech_mult=n), cc,
                                 f'mult={mult}')

plt.show()
