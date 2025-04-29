from pathlib import Path
import pickle

import matplotlib
import matplotlib.pyplot as plt

import netpyne_res_parse_utils as parse_utils


dirpath_base = Path(
    r'D:\WORK\Salvador\repo\A1_OUinp\exp_results\batch_i_ougrid_its4_20x20_tau_10'
    #r'D:\WORK\Salvador\repo\A1_OUinp\exp_results\batch_ougrid_vip_0'
)

sim_name = 'batch_i_ougrid_its4_20x20_med_00236'
#sim_name = 'batch_ougrid_vip_0_00290'

pop_vis = 'ITS4'
#pop_vis = 'VIP5A'


# Load sim result
fpath_sim_res = dirpath_base / f'{sim_name}_data.pkl'
with open(fpath_sim_res, 'rb') as fid:
    sim_res = pickle.load(fid)

# Extract voltages
V_data, _ = parse_utils.get_voltages(sim_res, t_limits=(2000, 3000))

matplotlib.use('Qt5Agg', force=True)

# Plot voltage histogram
#plt.ion()
plt.figure()
plt.hist(V_data[pop_vis].ravel(), bins=50, color='blue', alpha=0.7)
plt.title(f'Histogram of {pop_vis} voltages')
plt.xlabel('Voltage (mV)')
plt.draw()
plt.show()