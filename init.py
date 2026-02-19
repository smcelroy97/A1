import json
import os
from pathlib import Path
import pickle as pkl

import matplotlib
import matplotlib.pyplot as plt
#matplotlib.use('Agg')  # to avoid graphics error on servers
import numpy as np
import pandas

from netpyne.batchtools import comm, specs
from netpyne import sim

from netParams import cfg, netParams
from post_run import post_run

import background_stim_new as bs
from collect_cell_gids import _collect_cell_gids
import warnings

warnings.simplefilter('once')

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
               'path': path,
               'csv': csv_name}

    print(message)

    return message
# save .json

if sim.rank == 0: # allSimData only exists on node 0... only one node should be performing analysis and file op...
    message = sim_analysis()
    sim.send(message)

# Finalize
