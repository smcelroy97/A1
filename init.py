import json
import os
from pathlib import Path
import pickle as pkl

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')  # to avoid graphics error on servers
import numpy as np
import pandas as pd

from netpyne.batchtools import comm, specs
from netpyne import sim

from netParams_new import cfg, netParams
from post_run import post_run

import background_stim_new as bs
from collect_cell_gids import _collect_cell_gids


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

dirpath_self = Path(__file__).resolve().parent

comm.initialize()

# Create a folder for the results
os.makedirs(cfg.saveFolder, exist_ok=True)

# Save cfg and netParams into the output folder
if comm.is_host():
    fpath_cfg = "{}/{}_cfg.json".format(cfg.saveFolder, cfg.simLabel)
    print(f'Saving to {fpath_cfg}', flush=True)
    cfg.save(fpath_cfg)
    netParams.save('{}/{}_netParams.json'.format(cfg.saveFolder, cfg.simLabel))

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
setdminID(sim, ['IT5A'])

# Set cell locations for cochlear cells

# Create connections and external inputs
sim.net.connectCells()      # create connections between cells based on params
#print('Adding stims...', flush=True)
sim.net.addStims() 			# add network stimulation

import warnings
warnings.simplefilter('once')

# Extract min/max cell gid for every pop. across ranks into sim._pop_gid_range
_collect_cell_gids()

# Setup variables to record for each cell (spikes, V traces, etc)
sim.setupRecording()

# Add OU current or conductance input to each Cell
#ctrl_dict = None
sim, vecs_dict = bs.add_noise_iclamp(sim)



#if sim.cfg.add_ou_current: # always 1
#    if hasattr(sim.cfg, 'ou_ctrl_params'): # attribute does not exist
#        sim, vecs_dict, ctrl_dict = bs.add_noise_iclamp_ctrl(sim)
#    else:
#        sim, vecs_dict = bs.add_noise_iclamp(sim)
#if sim.cfg.add_ou_conductance:
#    sim, vecs_dict, OUFlags = bs.add_noise_gclamp(sim)

""" # Print ik mechs
if comm.is_host():
    hobj = sim.net.cells[0].secs['soma']['hObj']
    seg  = hobj(0.5)
    #print([name for name in dir(seg) if "ik" in name])
    print([name for name in dir(seg.kBK)])
    #print([name for name in seg.__dict__]) """

# Run
#if sim.rank == 0:
print(f'Rank {sim.rank}: running...', flush=True)
sim.runSim()               # run parallel Neuron simulation
#if sim.rank == 0:
#    print(f'Gathering the results...', flush=True)
sim.gatherData()

# Gather OUFlags
""" if sim.cfg.add_ou_conductance:
    allOUFlags = sim.pc.py_allgather(OUFlags)
    combinedOUFlags = {}
    for flags in allOUFlags:
        combinedOUFlags.update(flags)
    sim.OUFlags = combinedOUFlags """

# Gather controller traces
#if ctrl_dict is not None:
#    print('>>> Gather controller data...', flush=True)
#    ctrl_dict = bs.gather_ctrl_data(sim, ctrl_dict)

# Save and plot the result
sim.saveData()
sim.analysis.plotData()    # plot spike raster etc

# Finalize
if comm.is_host():
    #netParams.save("{}/{}_params.json".format(cfg.saveFolder, cfg.simLabel))
    print('transmitting data...')
    inputs = specs.get_mappings()
    
    # Save average firing rates to a separate json file
    avgRates = sim.analysis.popAvgRates(
        tranges=[cfg.duration - 1000, cfg.duration],
        show=False
    )
    fpath_res = '{}/{}_result.json'.format(cfg.saveFolder, cfg.simLabel)
    with open(fpath_res, 'w') as fid:
        json.dump({'rates': avgRates}, fid, indent=4)
    
    # Save controller data
    #if ctrl_dict is not None:
    #    fpath_res = '{}/{}_ctrl.pkl'.format(cfg.saveFolder, cfg.simLabel)
    #    with open(fpath_res, 'wb') as fid:
    #        pkl.dump(ctrl_dict, fid)

    # Plot controller signals and save the figures
    #if ctrl_dict is not None:
    #    bs.plot_save_ctrl_traces(sim, ctrl_dict)
    
    # Experiment-specific result processing
    # TODO

    avgRates['loss'] = 700
    out_json = json.dumps({**inputs, **avgRates})
    comm.send(out_json)
    comm.close()

    # Plot and save f-I curves
    post_run(sim)