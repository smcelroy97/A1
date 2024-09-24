import numpy as np
import matplotlib.pyplot as plt
import scipy
from sklearn.decomposition import PCA
from scipy import interpolate
from netpyne import sim

sim.initialize()
all = sim.loadAll('/Users/scoot/A1ProjData/A1_sim_data/v34_batch56_0_0_data.pkl')

simCSD = sim.analysis.prepareCSD(timeRange = [3400, 3600])
simCSD = simCSD[0]

mask_sinks = simCSD < 0
mask_sources = simCSD > 0

sinks = np.zeros((simCSD.shape[0], simCSD.shape[1]))
sources = np.zeros((simCSD.shape[0], simCSD.shape[1]))

sinks[mask_sinks] = np.abs(simCSD[mask_sinks])
sources[mask_sources] = np.abs(simCSD[mask_sources])

sinks_trial_avg = sinks/sinks.sum()
sources_trial_avg = sources/sources.sum()