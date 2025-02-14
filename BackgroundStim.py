import json

import h5py.h5d
import numpy as np

# adapted from: https://github.com/BlueBrain/neurodamus/blob/2c7052096c22fb5183fdef120d080608748da48d/neurodamus/core/stimuli.py#L271
class addStim():
    @staticmethod
    def add_ornstein_uhlenbeck(tau, sigma, mean, duration, dt=0.025, seed=100000, plotFig=False):
        from neuron import h
        import numpy as np
        from math import sqrt, exp
        """
        Adds an Ornstein-Uhlenbeck process with given correlation time,
        standard deviation and mean value.

        tau: correlation time [ms], white noise if zero
        sigma: standard deviation [uS]
        mean: mean value [uS]
        duration: duration of signal [ms]
        dt: timestep [ms]
        """

        """Creates a default RNG, currently based on ACG"""
        rng = h.Random(seed)
        tvec = h.Vector(np.linspace(0, duration, int(duration / dt)))
        ntstep = len(tvec)  # total number of timesteps

        svec = h.Vector(ntstep, 0)  # stim vector

        noise = h.Vector(ntstep)  # Gaussian noise
        rng.normal(0.0, 1.0)
        noise.setrand(rng)  # generate Gaussian noise

        if tau < 1e-9:
            svec = noise.mul(sigma)  # white noise
        else:
            mu = exp(-dt / tau)  # auxiliar factor [unitless]
            A = sigma * sqrt(1 - mu * mu)  # amplitude [uS]
            noise.mul(A)  # scale noise by amplitude [uS]

            # Exact update formula (independent of dt) from Gillespie 1996
            for n in range(1, ntstep):
                svec.x[n] = svec[n - 1] * mu + noise[n]  # signal [uS]


        svec.add(mean)  # shift signal by mean value [uS]

        if plotFig:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(30, 5))
            plt.plot(list(tvec), list(svec), 'k')
            plt.savefig('test_fig_vec_OrnsteinUhlenbeck.png')

            plt.figure(figsize=(30, 5))
            plt.plot(list(tvec)[0:1000], list(svec)[0:1000], 'k')
            plt.savefig('test_fig_vec_OrnsteinUhlenbeck_slice.png')

            plt.figure()
            plt.hist(list(svec), 100)
            plt.savefig('test_fig_vec_OrnsteinUhlenbeck_hist.png')

        return tvec, svec

    def addNoiseGClamp(sim):
        # from init import vecs_dict
        from neuron import h
        import numpy as np
        print('Creating Ornstein Uhlenbeck process to create noise conductance signal')
        import math
        vecs_dict = {}
        OUFlags = {}
        for cell_ind, cell in enumerate(sim.net.cells):
            pop = cell.tags['pop']
            if pop not in OUFlags:
                OUFlags[pop] = True
            vecs_dict.update({cell_ind: {'tvecs': {}, 'svecs': {}}})
            cell_seed = (sim.cfg.seeds['stim']+ cell.gid) * 2
            for stim_ind, stim in enumerate(sim.net.cells[cell_ind].stims):
                if 'NoiseSEClamp' in stim['label']:
                    mean = sim.net.params.NoiseConductanceParams[cell.tags['pop']]['g0']
                    sigma = sim.net.params.NoiseConductanceParams[cell.tags['pop']]['sigma']
                    tvec, svec = addStim.add_ornstein_uhlenbeck(
                        tau=10,
                        sigma=sigma,
                        mean=mean,
                        duration=stim['dur1'],
                        dt=0.05,
                        seed=cell_seed,
                        plotFig=False)

                    if any(val<0.0 for val in svec):
                        OUFlags[pop] = False
                        break
                    else:
                    # for idx, val in enumerate(svec):
                    #     if val < 0.0:
                    #         svec[idx] = 0.001
                        vecs_dict[cell_ind]['tvecs'].update({stim_ind: tvec})
                        vecs_dict[cell_ind]['svecs'].update({stim_ind: svec})

        for cell_ind, cell in enumerate(sim.net.cells):
            pop = cell.tags['pop']
            for stim_ind, stim in enumerate(sim.net.cells[cell_ind].stims):
                if 'NoiseSEClamp' in stim['label']:
                    if OUFlags[pop] == True:  # Check the flag for the population
                        conductance_source = sim.net.cells[cell_ind].stims[stim_ind]['hObj']
                        # stim_vec = h.Vector([1 / x if x > 1E-9 and x < 1E9 else 1E9 for x in vecs_dict[cell_ind]['svecs'][stim_ind]])
                        stim_vec = vecs_dict[cell_ind]['svecs'][stim_ind]
                        # stim_vecInv = h.Vector([1/x if x > 1E-9 and x < 1E9 else 1E9 for x in stim_vec])
                        stim_vec.play(conductance_source._ref_rs, vecs_dict[cell_ind]['tvecs'][stim_ind], 1)


        return sim, vecs_dict, OUFlags



    def addNoiseIClamp(sim):
        import numpy as np
        print('\t>> Using Ornstein Uhlenbeck to add noise to the IClamp')
        import math
        # from CurrentStim import CurrentStim as CS
        vecs_dict = {}
        for cell_ind, cell in enumerate(sim.net.cells):
            vecs_dict.update({cell_ind: {'tvecs': {}, 'svecs': {}}})
            cell_seed = sim.cfg.seeds['stim']+ cell.gid
            for stim_ind, stim in enumerate(sim.net.cells[cell_ind].stims):
                if 'NoiseIClamp' in stim['label']:
                    mean = sim.net.params.NoiseIClampParams[cell.tags['pop']]['g0']
                    variance = sim.net.params.NoiseIClampParams[cell.tags['pop']]['sigma']

                    tvec, svec = BackgroundStim.add_ornstein_uhlenbeck(
                        tau= 10,
                        sigma=variance,
                        mean=mean,
                        duration=stim['dur'],
                        dt=0.025,
                        seed=cell_seed,
                        plotFig=False)

                    vecs_dict[cell_ind]['tvecs'].update({stim_ind: tvec})
                    vecs_dict[cell_ind]['svecs'].update({stim_ind: svec})

                    vecs_dict[cell_ind]['svecs'][stim_ind].play(
                        sim.net.cells[cell_ind].stims[stim_ind]['hObj']._ref_amp, vecs_dict[cell_ind]['tvecs'][stim_ind],
                        True
                    )
        return sim, vecs_dict
