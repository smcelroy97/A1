import json
import os
from pathlib import Path
import pickle as pkl
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas
from netpyne.batchtools import comm, specs
from netpyne import sim
from netParams import cfg, netParams
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

# Create a folder for the results
os.makedirs(cfg.saveFolder, exist_ok=True)


# Initialize
sim.initialize(simConfig=cfg, netParams=netParams)

# Create populations
sim.net.createPops()

# Create cells
sim.net.createCells()

# Collect cells and pops
sim.net.allCells = [cell.__getstate__() for cell in sim.net.cells]
sim.net.allPops = {label: pop.__getstate__() for label, pop in sim.net.pops.items()}

track = sim
# Set min/max cell gid for each population
setdminID(sim, ['IT5A'])

# debug data
message = (f"minID output:\n"
           f"dminID: {sim.simData['dminID']}\n"
           f"dmaxID: {sim.simData['dmaxID']}\n"
           f"dnumc : {sim.simData['dnumc']}\n")

print(message)

# Set cell locations for cochlear cells

# Create connections and external inputs
sim.net.connectCells()      # create connections between cells based on params
sim.net.addStims() 			# add network stimulation

import warnings
warnings.simplefilter('once')

# Extract min/max cell gid for every pop. across ranks into sim._pop_gid_range
_collect_cell_gids()

# Setup variables to record for each cell (spikes, V traces, etc)
sim.setupRecording()

# Add OU current or conductance input to each Cell
sim, vecs_dict = bs.add_noise_iclamp(sim)

# Run
print(f'Rank {sim.rank}: running...', flush=True)
sim.runSim()               # run parallel Neuron simulation


sim.gatherData()

# Save and plot the result

path = f"{cfg.saveFolder}/{cfg.simLabel}"
sim.saveData()
sim.analysis.plotData()    # plot spike raster for viz.


# TODO James -- dummy functions --
# TODO Scott/Nikita create the relevant xarray/ .json file ...
# TODO Scott two firing rates (pre stimulus, post stimulus) for every cell
# please avoid any sim analysis functions/check if necessary

def sim_analysis():# don't need to pass
    """
    #TODO @nikita populate this function with whatever data needs can be calculated and stored ...
    sim_analysis takes sim object and calculates any notable values that can be gained from sim object
    #NOTES
    single numeric values and strings can be sent via message and collated in an sql/pandas structure for organization
    or, can save any larger values to desired format, and open them using path (unique to each job)
    """

    post_run(sim)

    # larger data structures can be stored in a separate file...
    spike_data = pandas.DataFrame({
        'gid': sim.allSimData['spkid'],
        'time': sim.allSimData['spkt']}
    )
    filtered_data = spike_data[(spike_data['gid']  > 100 ) & (spike_data['gid']  < 150 ) &
                               (spike_data['time'] > 1000) & (spike_data['time'] < 1500)]

    csv_name = f"{path}.csv"

    filtered_data.to_csv(csv_name)

    message = {'hbm0': cfg.ou_ramp_offset, # basic hbm values
               'hbm1': cfg.bkg_r,
               'hbm2': cfg.bkg_w,
               'hbm3': len(sim.allSimData['spkt']),
               'path': path,
               'csv': csv_name}

    print(message)

    return message
# save .json
if sim.rank == 0: # allSimData only exists on node 0... only one node should be performing analysis and file op...
    message = sim_analysis()
    sim.send(message)

# Finalize
