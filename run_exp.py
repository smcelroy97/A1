import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # to avoid graphics error on servers

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

# Take batch flag from command line arguments, default to False
parser = argparse.ArgumentParser(description="Run experiment script.")
parser.add_argument('--batch', action='store_true',
                    help="Run in batch mode.")
parser.add_argument('--name', type=str,
                    help="Experiment name (required if not in batch mode).")
args, _ = parser.parse_known_args()
is_batch = args.batch

if not args.batch and args.name is None:
    raise ValueError("Either --name or --batch is requred")

need_run = True

# Experiment name (define the folder name in exp_configs and exp_results)
if not is_batch:
    exp_name = args.name


dirpath_self = Path(__file__).resolve().parent

if is_batch:
    # Get simLabel from batchtools to identify exp_name,
    # which is then used to generate the path to exp_cfg.py
    exp_name = specs.mappings['simLabel'][:-6]  # cut away job id

# Import experiment-specific config and batch py-files
fpath_exp_cfg = dirpath_self / DIRNAME_EXP_CONFIGS / exp_name / 'exp_cfg.py'
fpath_exp_batch = dirpath_self / DIRNAME_EXP_CONFIGS / exp_name / 'batch_params.py'
#print(f'Experiment config: {fpath_exp_cfg}')
cfg_mod = load_module(fpath_exp_cfg)
if is_batch:
    batch_mod = load_module(fpath_exp_batch)

# Initialize config object, common for every experiment of the model
cfg = create_base_cfg()

# Apply experiment-specific config modifications
cfg_mod.apply_exp_cfg(cfg)

if not is_batch:
    # Automatically set the experiment name in config
    cfg.simLabel = exp_name
    cfg.saveFolder = str(dirpath_self / DIRNAME_EXP_RESULTS / exp_name)

# Update config by batchtools (if applicable)
cfg.update_cfg()

# Apply experiment-specific post-update config modifications
# (derive other params from the ones set by batchtools in update_cfg)
if is_batch and hasattr(batch_mod, 'post_update'):
    batch_mod.post_update(cfg)

# Create netParams based on the config
netParams = create_net_params(cfg)

comm.initialize()

# Save cfg and netParams into the output folder
if comm.is_host():
    cfg.save("{}/{}_cfg.json".format(cfg.saveFolder, cfg.simLabel))
    netParams.save('{}/{}_netParams.json'.format(cfg.saveFolder, cfg.simLabel))

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
    if sim.cfg.addNoiseConductance:
        sim, vecs_dict, OUFlags = BS.addStim.addNoiseGClamp(sim)

    # Run
    sim.setupRecording()       # setup variables to record for each cell (spikes, V traces, etc)
    sim.runSim()               # run parallel Neuron simulation
    sim.gatherData()

    # Gather OUFlags
    if sim.cfg.addNoiseConductance:
        allOUFlags = sim.pc.py_allgather(OUFlags)
        combinedOUFlags = {}
        for flags in allOUFlags:
            combinedOUFlags.update(flags)
        sim.OUFlags = combinedOUFlags

    # Save and plot the result
    sim.saveData()
    sim.analysis.plotData()    # plot spike raster etc

# Finalize
if comm.is_host():
    netParams.save("{}/{}_params.json".format(cfg.saveFolder, cfg.simLabel))
    print('transmitting data...')
    inputs = specs.get_mappings()
    avgRates = sim.analysis.popAvgRates(
        tranges=[cfg.duration - 1000, cfg.duration],
        show=False
    )
    avgRates['loss'] = 700
    out_json = json.dumps({**inputs, **avgRates})
    comm.send(out_json)
    comm.close()
