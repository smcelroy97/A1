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
from matplotlib import pyplot as plt
from input import cochlearInputSpikes
from netpyne import sim
from netParams import netParams, cfg
from analysis.simTools import simPlotting
import numpy as np
import BackgroundStim as BS
import json
import os
comm.initialize()

sim.initialize(simConfig = cfg, netParams = netParams)  		# create network object and set cfg and net params
sim.net.createPops()               			# instantiate network populations
sim.net.createCells()              			# instantiate network cells based on defined populations

sim.net.allCells = [cell.__getstate__() for cell in sim.net.cells]
sim.net.allPops = {label: pop.__getstate__() for label, pop in sim.net.pops.items()}

def setdminID (sim, lpop):
  # setup min,max ID and dnumc for each population in lpop
  alltags = sim._gatherAllCellTags() #gather cell tags; see https://github.com/Neurosim-lab/netpyne/blob/development/netpyne/sim/gather.py
  dGIDs = {pop:[] for pop in lpop}
  for tinds in range(len(alltags)):
    if alltags[tinds]['pop'] in lpop:
      dGIDs[alltags[tinds]['pop']].append(tinds)
  sim.simData['dminID'] = {pop:np.amin(dGIDs[pop]) for pop in lpop if len(dGIDs[pop])>0}
  sim.simData['dmaxID'] = {pop:np.amax(dGIDs[pop]) for pop in lpop if len(dGIDs[pop])>0}
  sim.simData['dnumc'] = {pop:np.amax(dGIDs[pop])-np.amin(dGIDs[pop]) for pop in lpop if len(dGIDs[pop])>0}

setdminID(sim, cfg.allpops)

def setCochCellLocationsX (pop, sz, scale):
  # set the cell positions on a line
  if pop not in sim.net.pops: return
  offset = sim.simData['dminID'][pop]
  ncellinrange = 0 # number of cochlear cells with center frequency in frequency range represented by this model
  sidx = -1
  for idx,cf in enumerate(netParams.cf):
    if cf >= cfg.cochThalFreqRange[0] and cf <= cfg.cochThalFreqRange[1]:
      if sidx == -1: sidx = idx # start index
      ncellinrange += 1
  if sidx > -1: offset += sidx
  for c in sim.net.cells:
    if c.gid in sim.net.pops[pop].cellGids:
      cf = netParams.cf[c.gid-sim.simData['dminID'][pop]]
      if cf >= cfg.cochThalFreqRange[0] and cf <= cfg.cochThalFreqRange[1]:
        c.tags['x'] = cellx = scale * (cf - cfg.cochThalFreqRange[0])/(cfg.cochThalFreqRange[1]-cfg.cochThalFreqRange[0])
        c.tags['xnorm'] = cellx / netParams.sizeX # make sure these values consistent
      else:
        c.tags['x'] = cellx = 100000000  # put it outside range for core
        c.tags['xnorm'] = cellx / netParams.sizeX # make sure these values consistent
      c.updateShape()

if cfg.cochlearThalInput: setCochCellLocationsX(
  'cochlea',
  netParams.popParams['cochlea']['numCells'],
  cfg.sizeX
)

sim.net.connectCells()      # create connections between cells based on params
sim.net.addStims() 			# add network stimulation

##########################################
# - Adding OU Noise Stims for each Cell -#
##########################################

if sim.cfg.addNoiseConductance:
  sim, vecs_dict, OUFlags = (
    BS.addStim.addNoiseGClamp(sim)
  )



sim.setupRecording()       # setup variables to record for each cell (spikes, V traces, etc)
sim.runSim()               # run parallel Neuron simulation
sim.gatherData()
sim.pc.barrier()

if sim.cfg.addNoiseConductance:
  allOUFlags = sim.pc.py_allgather(OUFlags)
  combinedOUFlags = {}
  for flags in allOUFlags:
    combinedOUFlags.update(flags)
  sim.OUFlags = combinedOUFlags

sim.saveData()
sim.analysis.plotData()    # plot spike raster etc

# Terminate batch process
if comm.is_host():
  if comm.rank == 0:
    netParams.save("{}/{}_params.json".format(cfg.saveFolder, cfg.simLabel))
    print('transmitting data...')
    inputs = specs.get_mappings()
    avgRates = sim.analysis.popAvgRates(tranges=[cfg.duration - 1000, cfg.duration], show=False)
    avgRates['loss'] = 700
    out_json = json.dumps({**inputs, **avgRates})

    figs, spikesDict = sim.analysis.plotSpikeStats(stats=['isicv', 'rate'], timeRange = [cfg.duration-1000, cfg.duration],saveFig=False, showFig=False, show=False)
    # simPlotting.plotMeanTraces(sim, cellsPerPop=1, plotPops=sim.cfg.allpops)

    # Define the file path for the JSON file
    json_file_path = f'../A1/simOutput/OUmapping_{cfg.simLabel}.json'

    # Ensure sim.cfg.OUamp and sim.cfg.OUstd are list-like
    ouamp_list = sim.cfg.OUamp if isinstance(sim.cfg.OUamp, (list, np.ndarray)) else [sim.cfg.OUamp]
    oustd_list = sim.cfg.OUstd if isinstance(sim.cfg.OUstd, (list, np.ndarray)) else [sim.cfg.OUstd]

    # Create new dictionaries for the data
    rate_dict = {pop: {oustd: {ouamp: None for ouamp in ouamp_list} for oustd in oustd_list} for pop in cfg.allpops}
    isicv_dict = {pop: {oustd: {ouamp: None for ouamp in ouamp_list} for oustd in oustd_list} for pop in cfg.allpops}

    # Populate the dictionaries with firing rates and isicv values
    for idx, pop in enumerate(cfg.allpops):
      for ouamp in ouamp_list:
        for oustd in oustd_list:
          if sim.OUFlags[pop] == False:
            print('Negative Resistance generated for ' + pop + '... data excluded from mapping')
            rate_dict[pop] = None
            isicv_dict[pop] = None
          else:
            rate_dict[pop]= avgRates[pop]
            isicv_dict[pop] = np.mean(spikesDict['statData'][idx + 1])

    # Save the dictionaries to the JSON file
    with open(json_file_path, 'w') as file:
      json.dump({'OUamp': cfg.OUamp, 'OUstd': cfg.OUstd, 'rate': rate_dict, 'isicv': isicv_dict}, file)

    comm.send(out_json)
    comm.close()

sim.close()
