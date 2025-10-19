# Adapted from: https://github.com/BlueBrain/neurodamus/blob/2c7052096c22fb5183fdef120d080608748da48d/neurodamus/core/stimuli.py#L271

#import json
from math import sqrt, exp

#import h5py.h5d
from neuron import h
import numpy as np


def generate_ou_signal(tau, sigma, mean, duration, dt=0.025,
                       seed=100000, plotFig=False,
                       invert_output=True, cutoff=1E-9,
                       verbose=False,
                       ramp_par=None,
                       ):
    """
    Generate an Ornstein-Uhlenbeck process with given correlation time,
    standard deviation and mean value.

    tau: correlation time [ms], white noise if zero
    sigma: standard deviation
    mean: mean value
    duration: duration of signal [ms]
    dt: timestep [ms]
    invert_output: return signal or 1/signal
    cutoff: lower cutoff value
    verbose: print debug info flag
    ramp_offset, ramp_mult, ramp_dur - initial ramp to suppress transients
    """

    # Create a default RNG, currently based on ACG
    rng = h.Random(seed)

    #print('generate_ou_signal(): create tvec and svec', flush=True)
    tvec_np = np.linspace(0, duration, int(duration / dt))
    tvec = h.Vector(tvec_np)
    ntstep = len(tvec)  # total number of timesteps
    svec = h.Vector(ntstep, 0)  # stim vector

    #print('generate_ou_signal(): create gaussian noise', flush=True)
    noise = h.Vector(ntstep)  # Gaussian noise
    rng.normal(0.0, 1.0)
    noise.setrand(rng)  # generate Gaussian noise

    if tau < 1e-9:
        svec = noise.mul(sigma)  # white noise
    else:
        mu = exp(-dt / tau)  # auxiliar factor [unitless]
        A = sigma * sqrt(1 - mu * mu)  # amplitude [uS]
        noise.mul(A)  # scale noise by amplitude [uS]
        # Generate zero-mean OU
        #print('generate_ou_signal(): generate OU signal', flush=True)
        for n in range(1, ntstep):
            svec.x[n] = svec[n - 1] * mu + noise[n]  # signal [uS]

    # Shift the signal by the mean value [uS]
    #print(f'generate_ou_signal(): add the mean (type={type(mean)})', flush=True)
    svec.add(mean)

    svec_np = np.array(svec, dtype=np.float64)

    # Ramp
    if (ramp_par is not None) and (ramp_par['dur'] is not None):
        t0, T = ramp_par['t0'], ramp_par['dur']
        tmask = (t0 <= tvec_np) & (tvec_np <= (t0 + T))
        ramp_len = np.sum(tmask)
        if ramp_par['type'] == 'down':
            ramp_off_vec = np.linspace(ramp_par['offset'], 0, ramp_len)
            ramp_mult_vec = np.linspace(ramp_par['mult'], 1, ramp_len)
        elif ramp_par['type'] == 'up':
            ramp_off_vec = np.linspace(0, ramp_par['offset'], ramp_len)
            ramp_mult_vec = np.linspace(1, ramp_par['mult'], ramp_len)
        elif ramp_par['type'] == 'up_down':
            len1 = ramp_len // 2
            len2 = ramp_len - len1
            ramp_off_vec = np.concatenate((
                np.linspace(0, ramp_par['offset'], len1),
                np.linspace(ramp_par['offset'], 0, len2)
            ))
            ramp_mult_vec = np.concatenate((
                np.linspace(1, ramp_par['mult'], len1),
                np.linspace(ramp_par['mult'], 1, len2)
            ))
        else:
            raise ValueError('Unknown ramp type')
        svec_np[tmask] = svec_np[tmask] * ramp_mult_vec + ramp_off_vec

    # Remove small and negative values from the noise
    # (clamp to a small positive number smin)
    if cutoff:
        #print('generate_ou_signal(): cutoff', flush=True)
        mask_neg = (svec_np < cutoff)
        svec_np[mask_neg] = cutoff
        if verbose:
            print(f'Proportion of clamped OU values: {np.mean(mask_neg)}')

    # Take the inverse of the signal if needed
    if invert_output:
        #print('generate_ou_signal(): inverse', flush=True)
        svec_np = 1. / svec_np
    svec = h.Vector(svec_np)

    """ if plotFig:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(30, 5))
        plt.plot(list(tvec), list(svec), 'k')
        plt.savefig('test_fig_vec_OrnsteinUhlenbeck.png')

        plt.figure(figsize=(30, 5))
        plt.plot(list(tvec)[0:1000], list(svec)[0:1000], 'k')
        plt.savefig('test_fig_vec_OrnsteinUhlenbeck_slice.png')

        plt.figure()
        plt.hist(list(svec), 100)
        plt.savefig('test_fig_vec_OrnsteinUhlenbeck_hist.png') """
    
    #print('generate_ou_signal(): done', flush=True)

    return tvec, svec


def add_noise_gclamp(sim):
    """Generate and play OU conductance signal(s) for every cell. """

    vecs_dict = {}
    OUFlags = {}

    ramp_dur = sim.cfg.ou_ramp_dur if hasattr(sim.cfg, 'ou_ramp_dur') else None
    ramp_offset = sim.cfg.ou_ramp_offset if hasattr(sim.cfg, 'ou_ramp_offset') else 0
    ramp_mult = sim.cfg.ou_ramp_mult if hasattr(sim.cfg, 'ou_ramp_mult') else 0
    raise NotImplementedError('Ramp not supported for g OU')

    # Generate OU signal(s)
    #print(f'add_noise_gclamp(): create OU inputs (dt={sim.cfg.dt})', flush=True)
    for cell_ind, cell in enumerate(sim.net.cells):

        pop = cell.tags['pop']
        if pop not in OUFlags:
            OUFlags[pop] = True
        vecs_dict.update({cell_ind: {'tvecs': {}, 'svecs': {}}})
        cell_seed = (sim.cfg.seeds['stim'] + cell.gid) * 2

        for stim_ind, stim in enumerate(sim.net.cells[cell_ind].stims):
            if 'NoiseOU' in stim['label']:
                mean = sim.net.params.NoiseOUParams[cell.tags['pop']]['mean']
                sigma = sim.net.params.NoiseOUParams[cell.tags['pop']]['sigma']

                tvec, svec = generate_ou_signal(
                    tau=sim.cfg.ou_tau,
                    sigma=sigma,
                    mean=mean,
                    duration=stim['dur1'],
                    dt=sim.cfg.dt,
                    seed=cell_seed,
                    plotFig=False,
                    #ramp_offset=ramp_offset,
                    #ramp_mult=ramp_mult,
                    #ramp_dur=ramp_dur
                )

                """ if (cell_ind == 0) and (stim_ind == 0):
                    print(f'mean = {mean}')
                    print(f'sigma = {sigma}')
                    print(f'duration = {stim["dur1"]}') """

                if any(val < 0.0 for val in svec):
                    raise ValueError('Negative values in the conductance signal are not allowed')
                else:
                    vecs_dict[cell_ind]['tvecs'].update({stim_ind: tvec})
                    vecs_dict[cell_ind]['svecs'].update({stim_ind: svec})

    # Play the OU signals to the cells
    # (via "rs" variable of ConductanceSource.mod)
    #print(f'add_noise_gclamp(): play OU inputs', flush=True)
    for cell_ind, cell in enumerate(sim.net.cells):
        pop = cell.tags['pop']
        if not OUFlags[pop]:
            continue
        for stim_ind, stim in enumerate(cell.stims):
            if 'NoiseOU' in stim['label']:
                stim_vec = vecs_dict[cell_ind]['svecs'][stim_ind]
                stim_vec.play(
                    stim['hObj']._ref_rs,
                    vecs_dict[cell_ind]['tvecs'][stim_ind]
                )
                #if (cell_ind == 0) and (stim_ind == 0):
                #    print('play()')

    return sim, vecs_dict, OUFlags


def add_noise_iclamp(sim):
    """Generate and play OU current signal(s) for every cell. """

    vecs_dict = {}
    #print('add_noise_iclamp(): create OU inputs '
    #      f'(dt={sim.cfg.dt}, ou_tau={sim.cfg.ou_tau})')
    
    ramp_par = {
        't0': sim.cfg.ou_ramp_t0 if hasattr(sim.cfg, 'ou_ramp_t0') else 0,
        'dur': sim.cfg.ou_ramp_dur if hasattr(sim.cfg, 'ou_ramp_dur') else None,
        'offset': sim.cfg.ou_ramp_offset if hasattr(sim.cfg, 'ou_ramp_offset') else 0,
        'mult': sim.cfg.ou_ramp_mult if hasattr(sim.cfg, 'ou_ramp_mult') else 0,
        'type': sim.cfg.ou_ramp_type if hasattr(sim.cfg, 'ou_ramp_type') else 'down',
        'pops': sim.cfg.ou_ramp_pops if hasattr(sim.cfg, 'ou_ramp_pops') else None
    }

    for cell_ind, cell in enumerate(sim.net.cells):

        vecs_dict.update({cell_ind: {'tvecs': {}, 'svecs': {}}})
        cell_seed = sim.cfg.seeds['stim'] + cell.gid

        for stim_ind, stim in enumerate(cell.stims):
            if 'NoiseOU' in stim['label']:
                pop = cell.tags['pop']
                mean = sim.net.params.NoiseOUParams[pop]['mean']
                sigma = sim.net.params.NoiseOUParams[pop]['sigma']

                # Relative cell "position" in the pop (0 to 1)
                pop_gids = sim._pop_gid_range[pop]
                #print(f'GIDS: {pop_gids}')
                cell_pos = (cell.gid - pop_gids[0]) / (pop_gids[1] - pop_gids[0])

                if not np.isscalar(mean):
                    mean = mean[0] + cell_pos * (mean[1] - mean[0])
                if not np.isscalar(sigma):
                    sigma = sigma[0] + cell_pos * (sigma[1] - sigma[0])

                ramp_par_ = ramp_par
                if ramp_par and (ramp_par['pops'] is not None):
                    if pop not in ramp_par['pops']:
                        ramp_par_ = None

                tvec, svec = generate_ou_signal(
                    tau=sim.cfg.ou_tau,
                    sigma=sigma,
                    mean=mean,
                    duration=stim['dur'],
                    dt=sim.cfg.dt,
                    seed=cell_seed,
                    invert_output=False,
                    cutoff=None,   # don't prune negative values
                    plotFig=False,
                    ramp_par=ramp_par_
                )

                vecs_dict[cell_ind]['tvecs'].update({stim_ind: tvec})
                vecs_dict[cell_ind]['svecs'].update({stim_ind: svec})

                vecs_dict[cell_ind]['svecs'][stim_ind].play(
                    stim['hObj']._ref_amp,
                    vecs_dict[cell_ind]['tvecs'][stim_ind],
                    True   # continuous
                )
    
    return sim, vecs_dict


if __name__ == '__main__':

    # Load input resistances
    import json
    from pathlib import Path
    dirpath_self = Path(__file__).resolve().parent
    fpath_resist = dirpath_self / 'data' / 'inputResistances.json'
    with open(fpath_resist, 'rb') as f:
        inp_res = json.load(f)

    ou_amp = 1 * 1e-4
    ou_std = 1 * 1e-4

    pop = 'ITP4'    
    #Gin = 1 / inp_res[pop]
    Gin = 1

    tvec, svec = generate_ou_signal(
        tau=10,
        sigma=ou_std * Gin,
        mean=ou_amp * Gin,
        duration=3000,
        dt=0.05,
        seed=1111111,
        plotFig=False,
        invert_output=False,
        cutoff = -0.0001,
        verbose=True
    )
    tvec = np.array(tvec)
    svec = np.array(svec)

    print(f'Mean: {svec.mean() * 1e4}')
    print(f'Std: {svec.std() * 1e4}')
    print(f'Min.: {svec.min() * 1e4}')
    print(f'Max.: {svec.max() * 1e4}')