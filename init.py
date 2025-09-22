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
# from input import cochlearInputSpikes
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

setdminID(sim, sim.net.pops)

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

if sim.cfg.addNoiseIClamp:
    sim, vecs_dict = (
      BS.addStim.addNoiseIClamp(sim)
    )


sim.setupRecording()       # setup variables to record for each cell (spikes, V traces, etc)
sim.runSim()               # run parallel Neuron simulation
sim.gatherData()

if sim.cfg.addNoiseConductance:
  allOUFlags = sim.pc.py_allgather(OUFlags)
  combinedOUFlags = {}
  for flags in allOUFlags:
    combinedOUFlags.update(flags)
  sim.OUFlags = combinedOUFlags

sim.saveData()
sim.analysis.plotData()    # plot spike raster etc

# Terminate batch process
if sim.rank == 0:
  netParams.save("{}/{}_params.json".format(cfg.saveFolder, cfg.simLabel))
  print('transmitting data...')
  inputs = cfg.get_mappings()

  # Get spike times and cell tags
  spike_times = sim.simData['spkt']
  spike_gids = sim.simData['spkid']
  cell_tags = {cell.gid: cell.tags for cell in sim.net.cells}

  # Define pop lists
  Ipops = cfg.Ipops
  Epops = cfg.Epops

  # Only consider spikes in the last 2 seconds
  start_time = cfg.duration - 2000  # ms
  filtered_spikes = [(gid, t) for gid, t in zip(spike_gids, spike_times) if t >= start_time]

  results = {}
  pop_loss = {}
  pop_loss['Epops'] = {}
  pop_loss['Ipops'] = {}

  sim_time = 2.0  # seconds

  for pop in Ipops + Epops:
    pop_gids = [gid for gid, tags in cell_tags.items() if tags['pop'] == pop]
    pop_spikes = [gid for gid, t in filtered_spikes if gid in pop_gids]
    rate = len(pop_spikes) / (len(pop_gids) * sim_time) if len(pop_gids) > 0 else 0
    results[pop] = rate
    target = 5.0 if pop in Ipops else 1.0

  # Calculate MSE for E and I populations
  e_losses = [(results[pop] - 1.0) ** 2 for pop in Epops]
  i_losses = [(results[pop] - 5.0) ** 2 for pop in Ipops]

  results['e_loss_avg'] = np.mean(e_losses) if e_losses else 0
  results['i_loss_avg'] = np.mean(i_losses) if i_losses else 0
  results['loss'] = (results['e_loss_avg'] + results['i_loss_avg']) / 2

  out_json = json.dumps({**inputs, **results})
  sim.send(out_json)

sim.close()
