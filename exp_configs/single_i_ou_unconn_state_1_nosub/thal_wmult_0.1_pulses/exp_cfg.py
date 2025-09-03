import json
from pathlib import Path
import shutil
import sys

import numpy  as np

dirpath_repo_root = Path(__file__).resolve().parents[3]
dirpath_self = Path(__file__).resolve().parent
sys.path.append(str(dirpath_repo_root))
#sys.path.append(str(dirpath_self))

from analysis.ou_tuning import sim_res_proc_utils as proc


def apply_exp_cfg(cfg):

    # Duration
    cfg.duration = 5 * 1e3

    # Populations to use
    pops_active = ['TC', 'TCM', 'HTC', 'TI', 'TIM', 'IRE', 'IREM']

    # Subnet parameters
    cfg.subnet_build_flag = 1
    cfg.subnet_params = {
        'pops_active': pops_active,   
        'conns_frozen': 'all',   # all inputs are surrogate, no recurrent connections
        'fpath_frozen_rates': str(dirpath_self / 'target_state_1.csv'),   # surrogate input
    }

    # Global weight multiplier
    cfg.wmult = 0.1

    # Turn off subConn
    cfg.addSubConn = 0

    # OU current input
    cfg.add_ou_current = 1
    cfg.ou_common = 0
    cfg.ou_noise_duration = cfg.duration
    cfg.ou_tau = 10
    with open(dirpath_self / 'ou_inputs.json', 'r') as fid:
        cfg.ou_pop_inputs = json.load(fid)

    # Cell mechanisms to modify
    with open(dirpath_self / 'mech_changes_1.json', 'r') as fid:
        cfg.mech_changes = json.load(fid)

    if 'plotRaster' in cfg.analysis:
        cfg.analysis['plotRaster']['include'] = pops_active
    if 'plotSpikeStats' in cfg.analysis:
        cfg.analysis['plotSpikeStats']['include'] = pops_active
    if 'plotTraces' in cfg.analysis:
        cfg.analysis['plotTraces']['include'] = pops_active
    
    # Time range for rate and CV calculation
    #cfg.analysis['plotSpikeStats']['timeRange'] = [5000, cfg.duration]
    cfg.analysis['plotSpikeStats'] = False

    # Record voltage traces
    """ ncells_rec = 4
    ncells_plot = 2
    cfg.recordCells = [(pop, list(range(ncells_rec))) for pop in pops_active]
    cfg.recordTraces = {'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}}
    cfg.recordStep =  0.1
    cfg.analysis['plotTraces'] = {
        'include': [(pop, list(range(ncells_plot))) for pop in cfg.allpops],
        'timeRange': [1000, cfg.duration],
        'oneFigPer': 'cell', 'overlay': True,
        'saveFig': True, 'showFig': False, 'figSize': (18, 12)
    } """

    # Input pulses
    cfg.pulseSeqParams = {
        't0': 1500,
        'period': 200,
        'jitter': 10,
        'width': 50,
        'n_pulses': 1000,
        'rates': 1000,
        'pop': 'TCM',
        'weight': 1,
        'rand_type': 'norm',
        'ncells': 200,
        'convergence': 1
    }


def generate_pulse_spike_times(par, Tsim, dt):

    np.random.seed(111)
    t0, T, jit = par['t0'], par['period'], par['jitter']

    # If pulse rate is a scalar - repeat it for each pulse
    if np.isscalar(par['rates']):
        par['rates'] = [par['rates']] * par['n_pulses']

    # Generate pulse timings
    tpulse = [t0]
    for _ in range(1, par['n_pulses']):
        if par['rand_type'] == 'uni':
            t = tpulse[-1] + T + np.random.uniform(-jit, jit)
        elif par['rand_type'] == 'norm':
            t = tpulse[-1] + np.random.normal(T, jit)
        else:
            raise ValueError('Unknown rand_type for pulse sequence: %s' % par['rand_type'])
        tpulse.append(t)
    tpulse = np.asarray(tpulse)
    #print(f'PULSES: =============> {tpulse[:20]}', flush=True)

    # Discard pulses beyond Tsim
    n_pulses = len(tpulse < Tsim)
    par['n_pulses'] = n_pulses
    par['tpulse'] = tpulse[:n_pulses].tolist()
    par['rates'] = par['rates'][:n_pulses]

    # Time bins
    tvec = np.arange(0, Tsim, dt)
    Nt = len(tvec)

    # Generare firing rate timecourse
    rvec = np.zeros(Nt)
    for n, tp in enumerate(tpulse):
        mask = (tp <= tvec) & (tvec < (tp + par['width']))
        rvec[mask] = par['rates'][n]

    # Generate Poisson spikes
    ncells = par['ncells']
    S = (np.random.rand(ncells, Nt) < (rvec * dt / 1000))
    spike_times = [tvec[np.argwhere(S[n, :])].ravel().tolist()
                   for n in range(ncells)] 
    return spike_times


def modify_net_params(cfg, params):
    """Applied after netParams creation. """

    # Modify membrane mechanisms
    for v in cfg.mech_changes.values():
        secs_all = params.cellParams[v['pop']]['secs']
        if v['sec'] == 'all':
            secs = list(secs_all.values())
        else:
            secs = [secs_all[v['sec']]]
        for sec in secs:
            sec['mechs'][v['mech']][v['par']] *= v['mult']
            sec['mechs'][v['mech']][v['par']] += v['add']

    # Generate pulse spike times
    Tsim, dt = cfg.duration, cfg.dt
    par = cfg.pulseSeqParams
    pop_out = par['pop']
    spike_times = generate_pulse_spike_times(par, Tsim, dt)
    # Pulses: spike source
    params.popParams['PulseSeq'] = {
        'cellModel': 'VecStim',
        'numCells': par['ncells'],
        'spkTimes': spike_times,   
        'delay': 0
    }
    # Pulses: target
    params.connParams[f'PulseSeq->{pop_out}'] = {
        'preConds':  {'pop': 'PulseSeq'},
        'postConds': {'pop': pop_out},
        'convergence': par['convergence'],
        'sec': 'soma',
        'loc': 0.5,
        'weight': par['weight'],
        'delay': 1,
        'synMech': 'AMPA',
        'synsPerConn': 1
    }

    #if cfg.analysis['plotRaster']:
    #    cfg.analysis['plotRaster']['include'].append('PulseSeq')


def post_run(sim):
    """Called in the end of a job (after runnig and saving). """

    cfg = sim.cfg
    dirpath_base = Path(cfg.saveFolder)

    # Calculate rate and CV for each pop., save the result to json
    t_limits = (2, cfg.duration / 1000)
    nspikes_min = 3
    res = proc.calc_rates_and_cvs(sim, t_limits, nspikes_min)
    fpath_res = '{}/{}_result.json'.format(cfg.saveFolder, cfg.simLabel)
    with open(fpath_res, 'w') as fid:
        json.dump(res, fid, indent=4)
    
    # Generate a subfolder name
    dur = int(cfg.duration / 1000)
    pulse_par = cfg.pulseSeqParams
    pT, pdur, pjit, pjtype, pr, pw, pn, pc, ppop = (
        pulse_par['period'], pulse_par['width'], pulse_par['jitter'],
        pulse_par['rand_type'], pulse_par['rates'], pulse_par['weight'],
        pulse_par['ncells'], pulse_par['convergence'], pulse_par['pop'])
    if not np.isscalar(pr):
        pr = pr[0]
    dirname_sub = (f'sim_{dur}s_pulses_{ppop}_{pdur}_{pT}_jit_{pjit}_{pjtype}_'
                   f'w_{pw}_r_{pr}_n_{pn}_c_{pc}')
    
    # Move all json and png files to the subfolder
    dirpath_sub = dirpath_base / dirname_sub
    dirpath_sub.mkdir(exist_ok=True)
    for ext in ('*.json', '*.png', '*.pkl'):
        for file in dirpath_base.glob(ext):
            shutil.move(str(file), str(dirpath_sub / file.name))
