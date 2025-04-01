import importlib.util
import json
import os
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')  # to avoid graphics error on servers

from netpyne.batchtools import comm
from netpyne import sim

from create_base_cfg import create_base_cfg
from create_net_params import create_net_params


def _load_module(fpath_mod):
    """Load py-file as a module to acess its functions. """
    mod_spec = importlib.util.spec_from_file_location(
        'module.name', fpath_mod)
    mod = importlib.util.module_from_spec(mod_spec)
    sys.modules['module.name'] = mod
    mod_spec.loader.exec_module(mod)
    return mod


# Folder names for experiment configs and results (relative to this script)
DIRNAME_EXP_CONFIGS = 'exp_configs'
DIRNAME_EXP_RESULTS = 'exp_results'

# Experiment name (define the folder name in exp_configs and exp_results)
exp_name = 'test_wmult_0.01'

is_batch = False
need_run = True


dirpath_self = Path(__file__).resolve().parent

# Import experiment-specific config py-file
fpath_exp_cfg = dirpath_self / DIRNAME_EXP_CONFIGS / exp_name / 'exp_cfg.py'
cfg_mod = _load_module(fpath_exp_cfg)

# Initialize config object, common for every experiment of the model
cfg = create_base_cfg()

# Apply experiment-specific config modifications
cfg_mod.apply_exp_cfg(cfg)

# Automatically set the experiment name in config
cfg.simLabel = exp_name
cfg.saveFolder = str(dirpath_self / DIRNAME_EXP_RESULTS / exp_name)

# Create the output folder if it does not exist
os.makedirs(cfg.saveFolder, exist_ok=True)

# Update config by batchtools (if applicable)
cfg.update_cfg()

# Create netParams based on the config
netParams = create_net_params(cfg)

comm.initialize()

# Save cfg and netParams into the output folder
if comm.is_host():
    cfg.save("{}/{}_cfg.json".format(cfg.saveFolder, cfg.simLabel))
    netParams.save('{}/{}_netParams.json'.format(cfg.saveFolder, cfg.simLabel))

if need_run:    
    # Prepare simulation
    sim.initialize(simConfig=cfg, netParams=netParams)
    sim.net.createPops()               			# instantiate network populations
    sim.net.createCells()              			# instantiate network cells based on defined populations
    sim.net.connectCells()            			# create connections between cells based on params
    sim.net.addStims() 							# add network stimulation
    
    # Run simulation
    sim.setupRecording()              			# setup variables to record for each cell (spikes, V traces, etc)
    sim.runSim()                      			# run parallel Neuron simulation  
    sim.gatherData()                  			# gather spiking data and cell info from each node
    
    # Save the results
    sim.cfg.savePickle = 1
    sim.saveData(include=['simConfig', 'netParams', 'simData', 'net'])
    
    # Plot the result
    sim.analysis.plotData()         			# plot spike raster etc

# Close the communication with the batchtools master process
if is_batch and comm.is_host():
   out_json = json.dumps({'loss': 0})
   comm.send(out_json)
   comm.close()
