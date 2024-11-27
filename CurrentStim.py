import json
import numpy as np


# adapted from: https://github.com/BlueBrain/neurodamus/blob/2c7052096c22fb5183fdef120d080608748da48d/neurodamus/core/stimuli.py#L271
class CurrentStim():
    def add_ornstein_uhlenbeck(tau, sigma, mean, duration, dt=0.025, seed=100000, plotFig=False):
        from neuron import h
        import numpy as np

        """
        Adds an Ornstein-Uhlenbeck process with given correlation time,
        standard deviation and mean value.

        tau: correlation time [ms], white noise if zero
        sigma: standard deviation [uS]
        mean: mean value [uS]
        duration: duration of signal [ms]
        dt: timestep [ms]
        """
        from math import sqrt, exp

        """Creates a default RNG, currently based on ACG"""
        rng = h.Random(seed)

        # rng = RNG()  # Creates a default RNG
        # if not self._rng:
        #     logging.warning("Using a default RNG for Ornstein-Uhlenbeck process")

        # tvec = h.Vector()
        # tvec.indgen(self._cur_t, self._cur_t + duration, dt)  # time vector
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

        # self._add_point(self._base_amp)
        # self.time_vec.append(tvec)
        # self.stim_vec.append(svec)
        # self._cur_t += duration
        # self._add_point(self._base_amp)

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

                    # try:
                    mean = stim['amp']
                    variance = sim.cfg.NoiseIClampParams[cell.tags['pop']]['sigma']
                        # print('mean noise: ', mean, ' nA')
                    # except:
                    #     mean = 0
                        # print('except mean noise: ', mean, ' nA')

                    tvec, svec = CurrentStim.add_ornstein_uhlenbeck(
                        tau= 0, #1e-9,
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

    def addHoldingCurrent(sim):
        print('\t>> Adding cell-tuned values to HoldingCurrent stimulation')
        for cell_ind, cell in enumerate(sim.net.cells):
            cell_pop = sim.net.cells[cell_ind].tags['pop']
            for stim_ind, stim in enumerate(sim.net.cells[cell_ind].stims):
                if 'HoldingCurrent' in stim['label']:
                    try:
                        threshold_percent_multiplier = (sim.cfg.addHoldingCurrentPercent[cell_pop]) / 100
                        # --- Changing hObj value, which is the real value used during the simulation
                        sim.net.cells[cell_ind].stims[stim_ind]['hObj'].amp = (
                                threshold_percent_multiplier * sim.net.params.store_cell_properties[sim.net.cells[cell_ind].tags['label'][0]][
                            '@dynamics:holding_current'])
                        # --- Changing label too, so that it is stored with the new value for inspection
                        sim.net.cells[cell_ind].stims[stim_ind]['amp'] = (
                                threshold_percent_multiplier * sim.net.params.store_cell_properties[sim.net.cells[cell_ind].tags['label'][0]][
                            '@dynamics:holding_current'])
                    except:
                        print('Modifying HoldingCurrent failed for cell ', cell_ind, ' | stim ', stim_ind)
        return sim

    def addThresholdCurrent(sim):
        print('\t>> Adding cell-tuned values to ThresholdCurrent stimulation')
        vecs_dict = {}
        for cell_ind, cell in enumerate(sim.net.cells):
            vecs_dict.update({cell_ind: {'tvecs': {}, 'svecs': {}}})

            if 'cellModel' in cell.tags.keys(): continue  # skips VecStims and artificial cells
            cell_pop = sim.net.cells[cell_ind].tags['pop']

            # print(cell_pop, sim.net.cells[cell_ind].gid)

            # # --- Rescales each threshold current individually to account for differences in RMP when the holding and threshold currents are added to the cell
            # if sim.cfg.addCellTypeCompensation: compensation_multiplier = sim.cfg.compensation_multiplier[sim.net.cells[cell_ind].tags['label'][0]]
            # else:                               compensation_multiplier = 1

            for stim_ind, stim in enumerate(sim.net.cells[cell_ind].stims):
                if 'ThresholdCurrent' in stim['label']:
                    if sim.cfg.addModifyRMP_vecPlay:
                        # print('>> -- -- -- -- -- -- Adding vector play in the RMP for cell ', cell_ind, ' and stim ',stim_ind)
                        from neuron import h
                        init_t = 0
                        threshold_percent_multiplier = (sim.cfg.addThresholdCurrentPops_byCellTemplate[sim.net.cells[cell_ind].tags['label'][0]]) / 100

                        tvec = h.Vector(np.linspace(0, sim.cfg.duration, int(sim.cfg.duration / sim.cfg.dt)))
                        ntstep = len(tvec)  # total number of timesteps
                        svec = h.Vector(ntstep, threshold_percent_multiplier)  # stim vector

                        if len(sim.cfg.modifyRMP_vecPlay_dict['t']) > 0:
                            t_inds = [0]
                            s_vals = [threshold_percent_multiplier * sim.net.params.store_cell_properties[sim.net.cells[cell_ind].tags['label'][0]]['@dynamics:threshold_current']]
                            s_vals_new = [(s_val / 100) * sim.net.params.store_cell_properties[sim.net.cells[cell_ind].tags['label'][0]]['@dynamics:threshold_current'] for s_val in
                                          sim.cfg.modifyRMP_vecPlay_dict[sim.net.cells[cell_ind].tags['label'][0]]]
                            s_vals.extend(s_vals_new)

                            for t in sim.cfg.modifyRMP_vecPlay_dict['t']: t_inds.append(int(t / sim.cfg.dt))

                            # safety condition, to avoid errors during svec reassignment
                            if t_inds[-1] > (sim.cfg.duration / sim.cfg.dt):  # no need to add an extra point, because the assigned values extend beyond sim.cfg.duration
                                pass
                            else:
                                t_inds.extend([int(sim.cfg.duration / sim.cfg.dt)])  # extends with the last point of the simulation to avoid errors in svec update below
                                s_vals.extend([s_vals_new[-1]])  # extends with the last point of the simulation to avoid errors in svec update below

                        s_val_ind = 0
                        for s_ind in range(len(svec)):
                            if s_ind >= t_inds[s_val_ind + 1]: s_val_ind += 1
                            svec[s_ind] = s_vals[s_val_ind]

                        vecs_dict[cell_ind]['tvecs'].update({stim_ind: tvec})
                        vecs_dict[cell_ind]['svecs'].update({stim_ind: svec})

                        vecs_dict[cell_ind]['svecs'][stim_ind].play(sim.net.cells[cell_ind].stims[stim_ind]['hObj']._ref_amp, vecs_dict[cell_ind]['tvecs'][stim_ind], True)

                    else:
                        try:
                            # threshold_percent_multiplier = (sim.cfg.addThresholdCurrentPercent[cell_pop])/100
                            # threshold_percent_multiplier = compensation_multiplier*threshold_percent_multiplier

                            threshold_percent_multiplier = (sim.cfg.addThresholdCurrentPops_byCellTemplate[sim.net.cells[cell_ind].tags['label'][0]]) / 100

                            # --- Changing hObj value, which is the real value used during the simulation
                            sim.net.cells[cell_ind].stims[stim_ind]['hObj'].amp = threshold_percent_multiplier * sim.net.params.store_cell_properties[sim.net.cells[cell_ind].tags['label'][0]][
                                '@dynamics:threshold_current']
                            # --- Changing label too, so that it is stored with the new value for inspection
                            sim.net.cells[cell_ind].stims[stim_ind]['amp'] = threshold_percent_multiplier * sim.net.params.store_cell_properties[sim.net.cells[cell_ind].tags['label'][0]][
                                '@dynamics:threshold_current']
                        except:
                            print('Modifying ThresholdCurrent failed for cell ', cell_ind, ' | stim ', stim_ind)
        # return sim
        return sim, vecs_dict

    def addConnWeightVectorPlay_g(sim,
                                  connLabels=['conn|TRN|VPM|chem'],
                                  connWeight_vals=[[(2500, 0.15), (5000, 1.75), (7500, 1.0)]],
                                  # connLabels      = ['conn|TRN|VPM|chem', 'conn|TRN@biophysical|TRN@biophysical|chem'],
                                  # connWeight_vals = [[(2500,0.15),(5000,1.75),(7500,1.0)],[(2500,0.15),(5000,1.75),(7500,1.0)]],
                                  conversion_factor=0.001,  # from nS to uS
                                  ):
        print('\t>> -- -- -- -- -- -- Adding Vector Play method to syn mech conductance')
        from neuron import h
        try:
            modify_conns = list(sim.cfg.modifyConnWeight_vecPlay_dict.keys())
            modify_conns_g_vals = list(sim.cfg.modifyConnWeight_vecPlay_dict.values())
        except:
            modify_conns = connLabels
            modify_conns_g_vals = connWeight_vals

        modify_conns_dict = {modify_conns: modify_conns_g_vals[modify_conns_ind] for modify_conns_ind, modify_conns in enumerate(modify_conns)}

        # Creating a dictionary to store the vectors to be played
        store_vectors_dict = {}
        store_w0 = {}
        if len(modify_conns) == len(modify_conns_g_vals):
            for modify_conn_ind, modify_conn in enumerate(modify_conns):

                w0 = sim.net.params.connParams[modify_conn]['weight']  # weight assigned in <cfg>, before running <WeightNormalization.normalizeWeights>
                print(w0)
                store_w0.update({modify_conn: w0})

                tvec = h.Vector(np.linspace(0, sim.cfg.duration, int(sim.cfg.duration / sim.cfg.dt)))
                ntstep = len(tvec)  # total number of timesteps
                svec = h.Vector(ntstep, w0)  # stim vector

                t_inds = [0]
                t_vals = [t for t, g in modify_conns_g_vals[modify_conn_ind]]
                t_inds_ = [int(t / sim.cfg.dt) for t in t_vals]
                t_inds.extend(t_inds_)

                g_vals = [w0]
                g_vals_ = [g * conversion_factor for t, g in modify_conns_g_vals[modify_conn_ind]]  # warning: conversion_factor from nS to uS is added here
                g_vals.extend(g_vals_)

                # safety condition, to avoid errors during svec reassignment
                if t_inds[-1] > (sim.cfg.duration / sim.cfg.dt):  # no need to add an extra point, because the assigned values extend beyond sim.cfg.duration
                    pass
                else:
                    t_inds.extend([int(sim.cfg.duration / sim.cfg.dt)])  # extends with the last point of the simulation to avoid errors in svec update below
                    g_vals.extend([g_vals_[-1]])  # extends with the last point of the simulation to avoid errors in svec update below

                s_val_ind = 0
                for s_ind in range(len(svec)):
                    if s_ind >= t_inds[s_val_ind + 1]:
                        print(s_ind, s_val_ind, t_inds[s_val_ind], t_inds[s_val_ind + 1])
                        s_val_ind += 1
                    svec[s_ind] = g_vals[s_val_ind]

                store_vectors_dict.update({modify_conn: {'tvec': tvec, 'svec': svec}})

                plotfig = False
                if plotfig:
                    from matplotlib import pyplot as plt
                    plt.figure(figsize=(12, 6))
                    plt.plot(tvec, svec)
                    plt.savefig('test_weight_Svec_' + modify_conn + '.png')
        else:
            print('Number of mechanims and values do not match...\nIssue must be fixed')
            return sim, vecs_dict

        vecs_dict = {}
        store_gmax = []
        for cell_ind, cell in enumerate(sim.net.cells):
            # vecs_dict.update({cell_ind:{}})
            vecs_dict.update({cell_ind: {'tvecs': {}, 'svecs': {}}})
            if 'cellModel' in cell.tags.keys(): continue  # skips VecStims and artificial cells
            # print(cell_ind)
            cell_pop = sim.net.cells[cell_ind].tags['pop']

            for conn_ind, conn in enumerate(sim.net.cells[cell_ind].conns):
                # print(cell_ind,conn_ind)
                if conn['label'] in modify_conns:
                    t_v = store_vectors_dict[conn['label']]['tvec']
                    s_v = store_vectors_dict[conn['label']]['svec']

                    # # unpacks the weight value when <WeightNormalization.normalizeWeights> is applied to each conn based on the sec/loc where the synapse is placed
                    # conn_normalizationFactor = sim.net.cells[cell_ind].conns[conn_ind]['hObj'].weight[0]/store_w0[conn['label']]
                    # # conn_normalizationFactor = store_w0[conn['label']]/sim.net.cells[cell_ind].conns[conn_ind]['weight']

                    # # print(cell_ind, conn_ind, conn['label'], conn_normalizationFactor,'\t',sim.net.cells[cell_ind].conns[conn_ind]['weight'],'\t',store_w0[conn['label']])
                    # new_s_v = s_v.c() # creates a new vector that is a copy of s_v, to avoid re-multiplication of the same vector in memory
                    # new_s_v.mul(conn_normalizationFactor)
                    # # print(conn_ind,s_v[0],new_s_v[0])

                    # try:    print('cell: ', cell_ind, '\tconn: ',conn_ind,'\tgmax:',sim.net.cells[cell_ind].conns[conn_ind]['hObj'].syn().gmax,'\t weights: ', s_v[0], s_v[100000], s_v[200000], s_v[300000])
                    # except: print(sim.net.cells[cell_ind].conns[conn_ind]['hObj'].syn().gmax,'\t weights: ', s_v[0])

                    vecs_dict[cell_ind].update({conn_ind: {'tvec'}})
                    vecs_dict[cell_ind]['tvecs'].update({conn_ind: t_v})
                    vecs_dict[cell_ind]['svecs'].update({conn_ind: s_v})
                    # vecs_dict[cell_ind]['svecs'].update({conn_ind:new_s_v})

                    vecs_dict[cell_ind]['svecs'][conn_ind].play(sim.net.cells[cell_ind].conns[conn_ind]['hObj']._ref_weight[0], vecs_dict[cell_ind]['tvecs'][conn_ind], True)

                    '''
                    example of pointer to weight:
                    sim.net.cells[0].conns[301]['hObj']._ref_weight[0]
                    '''

        return sim, vecs_dict

    # def addSynMechVectorPlay_g(sim,
    #                            synMechs=['syn|TRN|TRN|inh'],
    #                            vals=[[(2500,0.15),(5000,1.75),(7500,1.0)]],
    #                         #    synMechs=['syn|TRN|TRN|inh', 'syn|TRN|VPM|inh'],
    #                         #    vals=[[(2500,0.15),(5000,1.75),(7500,1.0)],[(2500,0.15),(5000,1.75),(7500,1.0)]],
    #                            conversion_factor=0.001,                             # from nS to uS
    #                            ):
    #     print('\t>> Adding Vector Play method to syn mech conductance')
    #     from neuron import h
    #     vecs_dict={}
    #     # try:    g_vals = sim.cfg.modifyGABAg
    #     try:
    #         modify_synMechs         = list(sim.cfg.modifyMechWeight.keys())
    #         modify_synMechs_g_vals  = list(sim.cfg.modifyMechWeight.values())
    #         # g_vals = sim.cfg.modifyMechWeight
    #     except:
    #         modify_synMechs         = synMechs
    #         modify_synMechs_g_vals  = vals

    #     # Creating a dictionary to store the vectors to be played
    #     if len(modify_synMechs)==len(modify_synMechs_g_vals):
    #         threshold_percent_multiplier = (sim.cfg.addThresholdCurrentPops_byCellTemplate[sim.net.cells[cell_ind].tags['label'][0]])/100
    #         w0 = sim.cfg.
    #         tvec = h.Vector(np.linspace(0, sim.cfg.duration, int(sim.cfg.duration/sim.cfg.dt)))
    #         ntstep = len(tvec)  # total number of timesteps
    #         svec = h.Vector(ntstep, threshold_percent_multiplier)  # stim vector

    #         modify_synMechs_dict = {s_mech:modify_synMechs_g_vals[i_s_mech] for i_s_mech, s_mech in enumerate(modify_synMechs)}
    #     else:
    #         print('Number of mechanims and values do not match...\nIssue must be fixed')
    #         return

    #     store_gmax=[]
    #     for cell_ind, cell in enumerate(sim.net.cells):
    #         print(cell_ind)
    #         vecs_dict.update({cell_ind:{'tvecs':{},'svecs':{}}})
    #         if 'cellModel' in cell.tags.keys(): continue # skips VecStims and artificial cells
    #         cell_pop = sim.net.cells[cell_ind].tags['pop']

    #         for conn_ind, conn in enumerate(sim.net.cells[cell_ind].conns):
    #             # print(cell_ind,conn_ind)
    #             if conn['synMech'] in modify_synMechs_dict.keys():
    #                 modify_synMechs_dict[conn['synMech']]

    #             if conn['synMech'] in modify_synMechs:
    #                 print(cell_ind,conn_ind,conn['synMech'])
    #                 store_gmax.append(sim.net.cells[cell_ind].conns[conn_ind]['hObj'].syn().gmax)

    #                 '''
    #                 example of pointer to weight:
    #                 sim.net.cells[0].conns[301]['hObj']._ref_weight[0]
    #                 '''

    def addRiCurrent(sim):
        print('\t>> Adding cell-tuned values to RiCurrent stimulation')

        try:
            with open(sim.cfg.storeRiCurrents, 'r') as file:
                storeRiCurrents = json.load(file)
        except:
            with open('../stims/RiCurrent/mean_rmp_values.json', 'r') as file:
                storeRiCurrents = json.load(file)

        with open('../stims/RiCurrent/seclamp_ri.json', 'r') as file:
            store_input_resistance = json.load(file)

        # sim.cfg.rebalancingCurrentPercent
        scale_current = {
            'VPM__pop': 300,
            'TRN__pop': 900,
            'TRN_ring__pop': 600,
        }
        # scale_current={ # good
        #                 'VPM__pop':     100,
        #                 'TRN__pop':     900,
        #                 'TRN_ring__pop':600,
        #                }
        for cell_ind, cell in enumerate(sim.net.cells):
            if 'cellModel' in cell.tags.keys(): continue  # skips VecStims and artificial cells

            cell_pop = sim.net.cells[cell_ind].tags['pop']
            cell_ri = sim.net.cells[cell_ind].secs['soma_0']['hObj'](0.5).ri()
            cell_vRest = storeRiCurrents[str(cell_ind)]
            cell_vTarget = sim.cfg.addRiCurrentTargetVoltage[cell_pop]

            # # Method 1:
            # cell_iValue     = (cell_vTarget-(cell_vRest))/(cell_ri*scale_current[cell_pop])

            # Method 2:
            # soma_length = sim.net.cells[cell_ind].secs['soma_0']['geom']['L']*1e-4
            # soma_area   = ((((sim.net.cells[cell_ind].secs['soma_0']['geom']['diam']*1e-4)**2)*np.pi)/4)
            # soma_Ra     = sim.net.cells[cell_ind].secs['soma_0']['geom']['Ra']

            # soma_Res    = soma_Ra*soma_length/soma_area
            # soma_Curr = (cell_vTarget-(cell_vRest))/soma_Res

            # cell_res = sum([((sim.net.cells[cell_ind].secs[sec]['geom']['Ra'])*sim.net.cells[cell_ind].secs[sec]['geom']['L']*1e-4)/((((sim.net.cells[cell_ind].secs[sec]['geom']['diam']*1e-4)**2)*np.pi)/4) for sec in sim.net.cells[cell_ind].secs.keys()])
            # soma_Curr = (cell_vTarget-(cell_vRest))*1e6/soma_Res_ # (nA)

            # cell_res = sum([((sim.net.cells[cell_ind].secs[sec]['geom']['Ra'])*sim.net.cells[cell_ind].secs[sec]['geom']['L']*1e-4)/((((sim.net.cells[cell_ind].secs[sec]['geom']['diam']*1e-4)**2)*np.pi)/4) for sec in sim.net.cells[cell_ind].secs.keys()])

            cell_res = sum([sim.net.cells[cell_ind].secs[sec]['hObj'](0.5).ri() for sec in sim.net.cells[cell_ind].secs.keys()])
            cell_iValue = (cell_vTarget - (cell_vRest)) / (cell_res)
            # cell_iValue     = (cell_vTarget-(cell_vRest))/(cell_res*scale_current[cell_pop])

            # # Method 3:
            # # using input resistance measured using SEClamp
            # # store_input_resistance
            # cell_iValue     = (cell_vTarget-(cell_vRest))/(store_input_resistance[str(cell_ind)]*scale_current[cell_pop])

            soma_Curr = cell_iValue

            print('\t gid: ', cell_ind, '\t i val: ', soma_Curr, '\t| V target: ', cell_vTarget, ' | V rest: ', cell_vRest)

            for stim_ind, stim in enumerate(sim.net.cells[cell_ind].stims):
                if 'RiCurrent' in stim['label']:
                    # print('Modifying stim ', stim_ind, ' | iValue: ', soma_Curr)
                    try:
                        # --- Changing hObj value, which is the real value used during the simulation
                        sim.net.cells[cell_ind].stims[stim_ind]['hObj'].amp = soma_Curr
                        # --- Changing label too, so that it is stored with the new value for inspection
                        sim.net.cells[cell_ind].stims[stim_ind]['amp'] = soma_Curr
                        print('Adding RiCurrent to cell # ', sim.net.cells[cell_ind].gid, ' with value ', soma_Curr, ' (nA)\t V target: ', cell_vTarget, ' | V rest: ', cell_vRest)

                    except:
                        print('Modifying RiCurrent failed for cell ', cell_ind, ' | stim ', stim_ind)
        return sim

    def addRmpVoltageToSEClamp(sim):
        print('\t>> Adding SEClamp stimulation')

        try:
            with open(sim.cfg.storeRiCurrents, 'r') as file:
                storeRiCurrents = json.load(file)
        except:
            with open('../stims/RiCurrent/mean_rmp_values.json', 'r') as file:
                storeRiCurrents = json.load(file)

        for cell_ind, cell in enumerate(sim.net.cells):
            if 'cellModel' in cell.tags.keys(): continue  # skips VecStims and artificial cells
            for stim_ind, stim in enumerate(sim.net.cells[cell_ind].stims):
                if 'SEClamp' in stim['label']:
                    # print('Modifying stim ', stim_ind, ' | iValue: ', soma_Curr)
                    try:
                        # # --- Changing hObj value, which is the real value used during the simulation
                        # sim.net.cells[cell_ind].stims[stim_ind]['hObj'].amp2 = storeRiCurrents[str(cell_ind)]
                        # # --- Changing label too, so that it is stored with the new value for inspection
                        # sim.net.cells[cell_ind].stims[stim_ind]['amp2']      = storeRiCurrents[str(cell_ind)]

                        cell_res = sim.net.cells[cell_ind].secs['soma_0']['hObj'](0.5).ri()
                        # cell_res         = sum([sim.net.cells[cell_ind].secs[sec]['hObj'](0.5).ri() for sec in sim.net.cells[cell_ind].secs.keys()])
                        try:
                            # --- Changing hObj value, which is the real value used during the simulation
                            sim.net.cells[cell_ind].stims[stim_ind]['hObj'].rs = cell_res
                            print('Changing RS worked for hObj of cell ', sim.net.cells[cell_ind].gid)
                        except:
                            print('Changing RS failed for hObj')
                        try:
                            # --- Changing label too, so that it is stored with the new value for inspection
                            sim.net.cells[cell_ind].stims[stim_ind]['rs'] = cell_res
                        except:
                            print('Changing RS failed for netpyne dicts')

                        print('Adding SEClamp modification to cell # ', sim.net.cells[cell_ind].gid, ' with value ', storeRiCurrents[str(cell_ind)], ' (mV)')

                    except:
                        print('Modifying RiCurrent failed for cell ', cell_ind, ' | stim ', stim_ind)
        return sim

    def addSECalibratedIClamp(sim):
        print('\t>> Adding cell-tuned SEClamp i values to IClamp stimulation')

        with open('../stims/RiCurrent/_seclamp_i_peak.json', 'r') as file:
            peakCurrents = json.load(file)
        for cell_ind, cell in enumerate(sim.net.cells):
            if 'cellModel' in cell.tags.keys(): continue  # skips VecStims and artificial cells
            for stim_ind, stim in enumerate(sim.net.cells[cell_ind].stims):
                if 'CalibratedCurrent' in stim['label']:

                    try:
                        # --- Changing hObj value, which is the real value used during the simulation
                        sim.net.cells[cell_ind].stims[stim_ind]['hObj'].amp = -peakCurrents[str(cell_ind)]
                        # --- Changing label too, so that it is stored with the new value for inspection
                        sim.net.cells[cell_ind].stims[stim_ind]['amp'] = -peakCurrents[str(cell_ind)]
                        print('Adding CalibratedCurrent to cell # ', sim.net.cells[cell_ind].gid, ' with value ', -peakCurrents[str(cell_ind)], ' (nA)')

                    except:
                        print('Modifying CalibratedCurrent failed for cell ', cell_ind, ' | stim ', stim_ind)
        return sim


if __name__ == "__main__":
    import math

    mean_percect = 0.0  # percent of threshold current (or holding current, not sure)
    threshold_current = 0.039407827
    holding_current = 0.0488804

    mean = (mean_percect / 100) * threshold_current
    variance = 0.001

    tvec, svec = CurrentStim.add_ornstein_uhlenbeck(tau=1e-9, sigma=math.sqrt(variance), mean=mean, duration=10250.0, dt=0.025, seed=100000, plotFig=True)