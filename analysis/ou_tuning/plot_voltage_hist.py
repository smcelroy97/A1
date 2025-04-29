from pathlib import Path
import pickle

import matplotlib
import matplotlib.pyplot as plt

from batch_result_manager import BatchResultManager
import netpyne_res_parse_utils as parse_utils


dirpath_base = Path(
    r'D:\WORK\Salvador\repo\A1_OUinp\exp_results\batch_ougrid_ire_4x4'
)

params = {
    'ou_mean': 0.006,
    'ou_std': 0.01
}

pop_vis = 'IRE'

# Get path to the data by job params
batch_res_mgr = BatchResultManager(dirpath_base)
fpath_sim_res = batch_res_mgr.job_data_fpath_by_params(params)
print(fpath_sim_res)

# Load sim result
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