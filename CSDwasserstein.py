import numpy as np
import matplotlib.pyplot as plt
import scipy
from sklearn.decomposition import PCA
from scipy import interpolate
from netpyne import sim
import sys
sys.path.append('/Users/scoot/OEvent')


# sim.initialize()
# all = sim.loadAll(
#     '/Users/scoot/A1ProjData/A1_sim_data/v34_batch56_0_0_data.pkl'
# )


# Prepare CSD and select timeRange
simCSD = sim.analysis.prepareCSD(timeRange = [3400, 3600])
simCSD = simCSD[0]

# Mask the data for sinks and sources
mask_sinks = simCSD < 0
mask_sources = simCSD > 0

# Create empty array to be aplied to te masked sinks and sources
sinks = np.zeros((simCSD.shape[0], simCSD.shape[1]))
sources = np.zeros((simCSD.shape[0], simCSD.shape[1]))

# Put isolated sinks and sources on onto correctly shaped array
# for accurate laminar and temporal distribution
sinks[mask_sinks] = np.abs(simCSD[mask_sinks])
sources[mask_sources] = np.abs(simCSD[mask_sources])

# Normalize
sinks_trial_avg = sinks/sinks.sum()
sources_trial_avg = sources/sources.sum()
simCSDavg = simCSD/np.abs(simCSD).max()

# Flatten for PCA so each session is one componant
flattened_simCSDavg = simCSDavg.reshape(
    1, simCSDavg.shape[0] * simCSDavg.shape[1])

# Set up and run PCA on full dataset
n_components = flattened_simCSDavg.shape[0]
pca = PCA(n_components=n_components)
pca.fit(flattened_simCSDavg.T)
print(pca.explained_variance_ratio_)
