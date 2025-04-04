import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # to avoid graphics error on servers
import numpy as np

from netpyne.batchtools import comm, specs
from netpyne import sim

import BackgroundStim as BS
from create_base_cfg import create_base_cfg
from create_net_params import create_net_params
from load_module import load_module


def setdminID(sim, lpop):
    # Setup min, max ID and dnumc for each population in lpop
    # Gather cell tags; see https://github.com/Neurosim-lab/netpyne/blob/development/netpyne/sim/gather.py
    alltags = sim._gatherAllCellTags()
    dGIDs = {pop: [] for pop in lpop}
    for tinds in range(len(alltags)):
        if alltags[tinds]['pop'] in lpop:
            dGIDs[alltags[tinds]['pop']].append(tinds)
    sim.simData['dminID'] = {pop: np.amin(
        dGIDs[pop]) for pop in lpop if len(dGIDs[pop]) > 0}
    sim.simData['dmaxID'] = {pop: np.amax(
        dGIDs[pop]) for pop in lpop if len(dGIDs[pop]) > 0}
    sim.simData['dnumc'] = {pop: np.amax(
        dGIDs[pop]) - np.amin(dGIDs[pop]) for pop in lpop if len(dGIDs[pop]) > 0}

def setCochCellLocationsX(cfg, netParams, pop, sz, scale):
    # Set the cell positions on a line
    if pop not in sim.net.pops:
        return
    offset = sim.simData['dminID'][pop]
    ncellinrange = 0  # number of cochlear cells with center frequency in frequency range represented by this model
    sidx = -1
    for idx, cf in enumerate(netParams.cf):
        if cf >= cfg.cochThalFreqRange[0] and cf <= cfg.cochThalFreqRange[1]:
            if sidx == -1:
                sidx = idx  # start index
            ncellinrange += 1
    if sidx > -1:
        offset += sidx
    for c in sim.net.cells:
        if c.gid in sim.net.pops[pop].cellGids:
            cf = netParams.cf[c.gid-sim.simData['dminID'][pop]]
            if cf >= cfg.cochThalFreqRange[0] and cf <= cfg.cochThalFreqRange[1]:
                c.tags['x'] = cellx = (
                    scale * (cf - cfg.cochThalFreqRange[0]) /
                    (cfg.cochThalFreqRange[1] - cfg.cochThalFreqRange[0])
                )
                # make sure these values consistent
                c.tags['xnorm'] = cellx / netParams.sizeX
            else:
                # put it outside range for core
                c.tags['x'] = cellx = 100000000
                # make sure these values consistent
                c.tags['xnorm'] = cellx / netParams.sizeX
            c.updateShape()


# Folder names for experiment configs and results (relative to this script)
DIRNAME_EXP_CONFIGS = 'exp_configs'
DIRNAME_EXP_RESULTS = 'exp_results'    # without batchtools

exp_name = 'opt_batch_1'

# Import experiment-specific config and batch py-files
dirpath_self = Path(__file__).resolve().parent
fpath_exp_cfg = dirpath_self / DIRNAME_EXP_CONFIGS / exp_name / 'exp_cfg.py'
#print(f'Experiment config: {fpath_exp_cfg}')
cfg_mod = load_module(fpath_exp_cfg)

# Initialize config object, common for every experiment of the model
cfg = create_base_cfg()
cfg.sim_manager = {}

# Apply experiment-specific config modifications
cfg_mod.apply_exp_cfg(cfg)

# Update config by batchtools (if applicable)
cfg.update_cfg()

dirpath_res = cfg.saveFolder
sim_label = cfg.sim_manager['sim_label']
fpath_reqs = cfg.sim_manager['requests_file']

print(f'Job script started (label={sim_label})', flush=True)
print(f'File with sim requests: {fpath_reqs}', flush=True)
print(f'Output folder for the results: {dirpath_res}', flush=True)

# Set the sim label that was passed from SimManager
cfg.simLabel = sim_label

# Read the request
with open(fpath_reqs, 'r') as fid:
    sim_request = json.load(fid)[sim_label]

print('Request:')
print(sim_request)

# Get external input rates (for every pop) from the request
cfg.ou_pop_inputs = sim_request['input']
cfg.addConn = sim_request['connected']
cfg.wmult = sim_request['wmult']

# Create netParams based on the config
netParams = create_net_params(cfg)

comm.initialize()

# Save cfg and netParams into the output folder
if comm.is_host():
    cfg.save("{}/{}_cfg.json".format(cfg.saveFolder, cfg.simLabel))
    netParams.save('{}/{}_netParams.json'.format(cfg.saveFolder, cfg.simLabel))

need_run = True

if need_run:
    # Initialize
    sim.initialize(simConfig=cfg, netParams=netParams)

    # Create populations
    sim.net.createPops()

    # Create cells
    sim.net.createCells()

    # Collect cells and pops
    sim.net.allCells = [cell.__getstate__() for cell in sim.net.cells]
    sim.net.allPops = {label: pop.__getstate__()
                       for label, pop in sim.net.pops.items()}

    # Set min/max cell gid for each population
    setdminID(sim, cfg.allpops)

    # Set cell locations for cochlear cells
    if cfg.cochlearThalInput:
        setCochCellLocationsX(
            cfg,
            netParams,
            'cochlea',
            netParams.popParams['cochlea']['numCells'],
            cfg.sizeX
        )

    # Create connections and external inputs
    sim.net.connectCells()      # create connections between cells based on params
    sim.net.addStims() 			# add network stimulation

    # Add OU conductance input to each Cell
    if sim.cfg.add_ou_conductance:
        sim, vecs_dict, OUFlags = BS.addStim.addNoiseGClamp(sim)

    # Run
    sim.setupRecording()       # setup variables to record for each cell (spikes, V traces, etc)
    sim.runSim()               # run parallel Neuron simulation
    sim.gatherData()

    # Gather OUFlags
    if sim.cfg.add_ou_conductance:
        allOUFlags = sim.pc.py_allgather(OUFlags)
        combinedOUFlags = {}
        for flags in allOUFlags:
            combinedOUFlags.update(flags)
        sim.OUFlags = combinedOUFlags

    # Save and plot the result
    sim.saveData()
    sim.analysis.plotData()    # plot spike raster etc

print('Job script finished')

# Finalize
if comm.is_host():
   out_json = json.dumps({'loss': 0})
   comm.send(out_json)
   comm.close()
