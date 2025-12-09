import numpy as np
import scipy.signal as sig
import xarray as xr


def calc_xr_welch(X_in: xr.DataArray,
                  win_len=0.5, win_overlap=0.5, fmax=100,
                  fs=None, time_dim='time', **kwargs) -> xr.DataArray:
    """Calculate power using Welch method. """
    
    # The code below assumes that time is the last dimension
    if X_in.dims[-1] != time_dim:
        raise ValueError('Time should be the last dimension')
    
    # Sampling rate
    tt0 = X_in.coords[time_dim].values
    if fs is None:
        fs = round(1. / (tt0[1] - tt0[0]), 5)  # round to correct for numerical errors

    # Window and overlap in samples
    nperseg = round(win_len * fs)
    noverlap = round(win_overlap * win_len * fs)

    # Call welch() on a surrogate array to get the output frequencies
    xz = np.zeros(len(tt0))
    ff, _ = sig.welch(xz, fs=fs, nperseg=nperseg, noverlap=noverlap)

    # Wrapping function for welch() that returns a single variable (power)
    def f(X, fs, nperseg, noverlap):
        _, S = sig.welch(
            X, fs=fs, nperseg=nperseg, noverlap=noverlap, axis=-1)
        return S
    
    # Apply welch() to xr.DataArray (with dask support)
    W = xr.apply_ufunc(
        f, X_in,
        kwargs={'fs': fs, 'nperseg': nperseg, 'noverlap': noverlap},
        input_core_dims=[[time_dim]],
        output_core_dims=[['freq']],
        output_sizes={'freq': len(ff)},
        vectorize=False, dask='parallelized',
        output_dtypes=[np.float64]
    )
    W = W.assign_coords({'freq': ('freq', ff)})
    
    # Select freq. range of interest
    W = W.sel(freq=slice(None, fmax))
    return W


def calc_xr_tf(X_in: xr.DataArray,
                  win_len=0.5, win_overlap=0.5, fmax=100,
                  fs=None, time_dim='time', **kwargs) -> xr.DataArray:
    """Calculate complex-valued time-frequency transform. """
    
    # The code below assumes that time is the last dimension
    if (X_in.dims[-1] != time_dim):
        raise ValueError('Time should be the last dimension')
    
    # Sampling rate
    tt0 = X_in.coords[time_dim].values
    if fs is None:
        fs = round(1. / (tt0[1] - tt0[0]), 5)  # round to correct for numerical errors

    # Window and overlap in samples
    nperseg = round(win_len * fs)
    noverlap = round(win_overlap * win_len * fs)

    # Call sig.spectrogram() on a surrogate array to get the output
    # frequencies and time bins
    xz = np.zeros(len(tt0))
    ff, tt, _ = sig.spectrogram(
        xz, fs=fs, nperseg=nperseg, noverlap=noverlap)
    # Shift positions of W_ time bins to the closest X_in time bins
    idx = np.round(tt * fs).astype(int)
    tt = tt0[idx]

    # Wrapping function for sig.spectrogram() that returns a single variable
    def f(X, fs, nperseg, noverlap):
        _, _, S = sig.spectrogram(
            X, fs=fs, nperseg=nperseg, noverlap=noverlap, mode='complex', axis=-1)
        return S
    
    # Apply sig.spectrogram() to xr.DataArray's (with dask support)    
    W = xr.apply_ufunc(
        f, X_in,
        kwargs={'fs': fs, 'nperseg': nperseg, 'noverlap': noverlap},
        input_core_dims=[[time_dim]],
        output_core_dims=[['freq', 'time1']],
        #output_sizes={'freq': len(ff), 'time1': len(tt)},
        dask_gufunc_kwargs={'output_sizes': {'freq': len(ff), 'time1': len(tt)}},
        vectorize=False, dask='parallelized',
        output_dtypes=[np.complex128]
    )
    W = W.rename({'time1': 'time'})    
    W = W.assign_coords(
         {'freq': ('freq', ff), 'time': ('time', tt)})
    
    # Select freq. range of interest
    W = W.sel(freq=slice(0, fmax))
    return W    
    