"""
init.py

Starting script to run NetPyNE-based A1 model.


Usage:
    python init.py # Run simulation, optionally plot a raster


MPI usage:
    mpiexec -n 4 nrniv -python -mpi init.py


Contributors: ericaygriffith@gmail.com, salvadordura@gmail.com
"""
from netpyne.batchtools import specs, comm
import matplotlib; matplotlib.use('Agg')  # to avoid graphics error in servers
from input import cochlearInputSpikes
from netpyne import sim
from synapse_netParams import netParams, cfg
import numpy as np
import matplotlib.pyplot as plt
from netpyne.analysis import spikes_legacy
import BackgroundStim as BS
from analysis.simTools import editNet
import json

comm.initialize()

sim.initialize(simConfig = cfg,
               netParams = netParams)  		# create network object and set cfg and net params
sim.net.createPops()               			# instantiate network populations
sim.net.createCells()              			# instantiate network cells based on defined populations

sim.net.allCells = [cell.__getstate__() for cell in sim.net.cells]
sim.net.allPops = {label: pop.__getstate__() for label, pop in sim.net.pops.items()}

sim.net.connectCells()            			# create connections between cells based on params
sim.net.addStims() 							# add network stimulation

# ########################################################################################
# - Adding OU Nose Stims for each Cell
# ########################################################################################

if sim.cfg.addNoiseIClamp:
  sim, vecs_dict = BS.addStim.addNoiseIClamp(sim)

sim.setupRecording()              			# setup variables to record for each cell (spikes, V traces, etc)
sim.runSim()                                    # run parallel Neuron simulation

trace_analysis = {}

plotPops = []
for cell in sim.net.cells:
    for conn in cell.conns:
        if conn['weight'] >0:
            if cell.tags['pop'] not in plotPops:
                plotPops.append(cell.tags['pop'])

sim.gatherData()
sim.saveData()
sim.analysis.plotData()    # plot spike raster etc




basemV = {}
amp = {}
peak = {}

for pop in trace_analysis:
    basemV[pop] = trace_analysis[pop][0]
    if cfg.prePop in cfg.Epops + cfg.TEpops:
        peak_idx = np.array(trace_analysis[pop]).argmax()
    else:
        peak_idx = np.array(trace_analysis[pop]).argmin()
    peak[pop] = trace_analysis[pop][peak_idx]
    amp[pop]  = peak[pop] - basemV[pop]


dummy = [1,2,3]
# Terminate batch process
if comm.is_host():
  netParams.save("{}/{}_params.json".format(cfg.saveFolder, cfg.simLabel))
  print('transmitting data...')
  inputs = specs.get_mappings()
  # results = sim.analysis.popAvgRates(show=False)
  # results['loss'] = results[cfg.prePop + '_stim']
  results = amp
  # for pop in trace_analysis:
  #   results[pop]['basemV'] = basemV[pop]
  #   results[pop]['peak'] = peak[pop]
  #   results[pop]['amp'] = amp[pop]
  results['loss'] = 700
  out_json = json.dumps({**inputs, **results})

  print(out_json)

  comm.send(out_json)
  comm.close()

sim.close()
