import numpy as np
import xarray as xr


def _get_xr_coords_dict(
        X: xr.DataArray
        ) -> dict[str, tuple[str, np.ndarray]]:
    return {name: (c.dims[0], c.values) for name, c in X.coords.items()}


def epoch_xr_data(
        X: xr.DataArray,
        ev_times: list[float] | np.ndarray,
        trial_win: tuple[float, float], 
        time_coord: str = 'time'
        ):
    """ Create epoched xr.DataArray from ndarray X. """
    
    t = X.coords[time_coord].values
    dt = t[1] - t[0]
    
    # Calculate relative epoch time samples
    #t_trial = np.arange(trial_win[0], trial_win[1] + dt, dt)
    t_trial = np.arange(trial_win[0], trial_win[1], dt)
    nt_trial = len(t_trial)

    trial_win = np.array(trial_win)
    ev_times = np.array(ev_times)

    # Remove ev_times whose epochs don't fit the data
    mask = ((ev_times + trial_win[0] >= t[0]) &
            (ev_times + trial_win[1] < t[-1]))
    ev_times = ev_times[mask]
    
    # Allocate an xarray for epoched data
    ntrials = len(ev_times)
    dims_ep = ('trial', *X.dims)
    coords_in = _get_xr_coords_dict(X)
    coords_ep = {'trial': np.arange(ntrials),
                 'ev_time': ('trial', ev_times)} | coords_in
    time_dim = coords_in[time_coord][0]
    coords_ep[time_coord] = (time_dim, t_trial)
    # TODO: remove other coords associated with time dim
    Xep = xr.DataArray(np.nan, dims=dims_ep, coords=coords_ep)

    # Epoch the data
    for n, t0 in enumerate(ev_times):
        t0 = t[np.argmin(np.abs(t - t0))]
        #t_win = np.round((t0 + trial_win) / dt).astype(int)
        #t_win[1] = t_win[0] + nt_trial
        ind0 = np.round((t0 + trial_win[0] - t[0]) / dt).astype(int)
        t_win = (ind0, ind0 + nt_trial)
        x = X.isel({time_coord: slice(*t_win)}).values
        Xep.loc[dict(trial=n)].values[...] = x
    return Xep


if __name__ == '__main__':
    t = np.arange(1, 20, 0.02)
    X = np.zeros((3, len(t)))
    X[0, :] = t
    X[1, :] = t * 10
    X[2, :] = t * 100
    X = xr.DataArray(X, dims=['y', 'time'],
                     coords={'y': ['a', 'b', 'c'], 'time': t})
    print(X)

    Xep = epoch_xr_data(
        X, ev_times=[3, 5, 7, 11, 19], trial_win=(-0.2, 0.5), time_coord='time')
    print(Xep)
