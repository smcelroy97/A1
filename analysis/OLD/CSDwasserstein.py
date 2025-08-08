import numpy as np
import matplotlib.pyplot as plt
import scipy
from sklearn.decomposition import PCA
from scipy import interpolate
from netpyne import sim
import sys
import h5py
from scipy.signal import resample

def rdmat (fn,samprds=0):
  fp = h5py.File(fn,'r') # open the .mat / HDF5 formatted data
  if 'craw' in fp: # up-to-date format
    sampr = fp['craw']['adrate'][0][0] # sampling rate
    dat = fp['craw']['cnt'] # cnt record stores the electrophys data
  else: # older format
    sampr = fp['adrate'][0][0] # sampling rate
    dat = fp['cnt'] # cnt record stores the electrophys data
  print('fn:',fn,'sampr:',sampr,'samprds:',samprds)
  dt = 1.0 / sampr # time-step in seconds
  npdat = np.zeros(dat.shape)
  tmax = ( len(npdat) - 1.0 ) * dt # use original sampling rate for tmax - otherwise shifts phase
  dat.read_direct(npdat) # read it into memory; note that this LFP data usually stored in microVolt
  npdat *= 0.001 # convert microVolt to milliVolt here
  fp.close()
  if samprds > 0.0: # resample the LFPs
    dsfctr = sampr/samprds
    dt = 1.0 / samprds
    if dsfctr == int(sampr/samprds):
      siglen = max((npdat.shape[0],npdat.shape[1]))
      nchan = min((npdat.shape[0],npdat.shape[1]))
      npds = [] # zeros((int(siglen/float(dsfctr)),nchan))
      # print('npdat.shape:',npdat.shape)
      for i in range(nchan):
        print('int downsampling channel', i)
        npds.append(downsample(npdat[:,i], sampr, samprds))
    else:
      import scipy
      siglen = max((npdat.shape[0],npdat.shape[1]))
      nchan = min((npdat.shape[0],npdat.shape[1]))
      npds = [] # zeros((int(siglen/float(dsfctr)),nchan))
      # print('npdat.shape:',npdat.shape)
      for i in range(nchan):
        print('resampling channel', i)
        npds.append(scipy.signal.resample(npdat[:,i], int(siglen * samprds/sampr)))
    # print(dsfctr, dt, siglen, nchan, samprds, ceil(int(siglen / float(dsfctr))), len(npds),len(npds[0]))
    npdat = np.array(npds)
    npdat = npdat.T
    sampr = samprds
  tt = np.linspace(0,tmax,len(npdat)) # time in seconds
  return sampr,npdat,dt,tt # npdat is LFP in units of milliVolt

# sim.initialize()
# all = sim.loadAll(
#     '/Users/scoot/A1ProjData/A1_sim_data/v34_batch56_0_0_data.pkl'
# )


# Prepare CSD and select timeRange
# simCSD = sim.analysis.prepareCSD(timeRange = [3400, 3600])
# simCSD = simCSD[0]

fn = '/Users/scoot/A1ProjData/A1_exp_data/2-um070071032@os.mat'

sampr,npdat,dt,tt  = rdmat(fn = fn)
def downsample(data, original_rate, target_rate):
    """
    Downsample the data from the original sampling rate to the target sampling rate.

    Parameters:
    data (numpy array): The input data to be downsampled.
    original_rate (int): The original sampling rate of the data.
    target_rate (int): The target sampling rate.

    Returns:
    numpy array: The downsampled data.
    """
    num_samples = int(len(data) * target_rate / original_rate)
    downsampled_data = resample(data, num_samples)
    return downsampled_data, target_rate

medthresh = 4.0 # median threshold
winsz = 1 # 10 second window size
freqmin = 0.25 # minimum frequency (Hz)
freqmax = 80.0  # maximum frequency (Hz)
freqstep = 0.25 # frequency step (Hz)
overlapth = 0.5 # overlapping bounding box threshold (threshold for merging event bounding boxes)
chan =  1 # npdat.shape[1]# which channel to use for event analysis
lchan = list(range(0, chan)) # list of channels to use for event analysis
MUA = None # multiunit activity; not required

dsdat, sampr = downsample(npdat, sampr,1250)

# s2,g,i1 = getflayers(fn, abbrev=True)
#
#
# # Mask the data for sinks and sources
# mask_sinks = simCSD < 0
# mask_sources = simCSD > 0
#
# # Create empty array to be aplied to te masked sinks and sources
# sinks = np.zeros((simCSD.shape[0], simCSD.shape[1]))
# sources = np.zeros((simCSD.shape[0], simCSD.shape[1]))
#
# # Put isolated sinks and sources on onto correctly shaped array
# # for accurate laminar and temporal distribution
# sinks[mask_sinks] = np.abs(simCSD[mask_sinks])
# sources[mask_sources] = np.abs(simCSD[mask_sources])
#
# # Normalize
# sinks_trial_avg = sinks/sinks.sum()
# sources_trial_avg = sources/sources.sum()
# simCSDavg = simCSD/np.abs(simCSD).max()
#
# # Flatten for PCA so each session is one componant
# flattened_simCSDavg = simCSDavg.reshape(1, simCSDavg.shape[0] * simCSDavg.shape[1])
#
# # Set up and run PCA on full dataset
# n_components = flattened_simCSDavg.shape[0]
# pca = PCA(n_components=n_components)
# pca.fit(flattened_simCSDavg.T)
# print(pca.explained_variance_ratio_)
