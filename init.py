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
import matplotlib;
matplotlib.use('Agg')  # to avoid graphics error in servers
from netpyne import sim
from netParams import netParams, cfg
import numpy as np
import BackgroundStim as BS
import json
import os

comm.initialize()

sim.initialize(simConfig = cfg,
               netParams = netParams)  		# create network object and set cfg and net params
sim.net.createPops()               			# instantiate network populations
sim.net.createCells()              			# instantiate network cells based on defined populations

# sim.net.allCells = [cell.__getstate__() for cell in sim.net.cells]
# sim.net.allPops = {label: pop.__getstate__() for label, pop in sim.net.pops.items()}

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

# updating a json with result values because the current batchtools format generates a big string of results
def append_to_json(file_path, new_data):
  # Check if the file exists
  if os.path.exists(file_path):
    # Read the existing data
    with open(file_path, 'r') as file:
      data = json.load(file)
  else:
    # Initialize an empty list if the file does not exist
    data = {}

  # Append the new data
  # data[sim.cfg.simLabel] = new_data
  data = new_data
  # Write the updated data back to the file
  with open(file_path, 'w') as file:
    json.dump(data, file)

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
  # print('setCochCellLocations: sidx, offset, ncellinrange = ', sidx, offset, ncellinrange)
  for c in sim.net.cells:
    if c.gid in sim.net.pops[pop].cellGids:
      cf = netParams.cf[c.gid-sim.simData['dminID'][pop]]
      if cf >= cfg.cochThalFreqRange[0] and cf <= cfg.cochThalFreqRange[1]:
        c.tags['x'] = cellx = scale * (cf - cfg.cochThalFreqRange[0])/(cfg.cochThalFreqRange[1]-cfg.cochThalFreqRange[0])
        c.tags['xnorm'] = cellx / netParams.sizeX # make sure these values consistent
        # print('gid,cellx,xnorm,cf=',c.gid,cellx,cellx/netParams.sizeX,cf)
      else:
        c.tags['x'] = cellx = 100000000  # put it outside range for core
        c.tags['xnorm'] = cellx / netParams.sizeX # make sure these values consistent
      c.updateShape()

if cfg.cochlearThalInput: setCochCellLocationsX(
  'cochlea',
  netParams.popParams['cochlea']['numCells'],
  cfg.sizeX
)


sim.net.connectCells()            			# create connections between cells based on params
sim.net.addStims() 							# add network stimulation

################################
# - Adding OU Noise Stims for each Cell -#
# ###############################

if sim.cfg.addNoiseConductance:
  sim, vecs_dict = BS.addStim.addNoiseGClamp(sim)



sim.setupRecording()              	 		# setup variables to record for each cell (spikes, V traces, etc)
sim.runSim()                                    # run parallel Neuron simulation
sim.gatherData()
sim.saveData()
sim.analysis.plotData()    # plot spike raster etc

plotPops = sim.cfg.allpops
rmpPops  = {}
for pop_ind, pop in enumerate(plotPops):
  print('\n\n', pop)
  # sim.analysis.plotTraces(
  figs, traces_dict = sim.analysis.plotTraces(
    include=[pop],
    # include=[record_pops[pop_ind]],
    # timeRange=[2500, 3000],
    # overlay=True, oneFigPer='trace',
    # ylim=[-90, -40],
    axis=True,
    # figSize=(70, 15),
    figSize=(25, 15),
    # figSize=(60, 18),
    fontSize=15,
    # saveFig=False,
    # saveFig=sim.cfg.saveFigPath+'/'+sim.cfg.filename+'_traces_'+pop+ '.png'
    saveFig=sim.cfg.saveFolder + '/' + sim.cfg.simLabel + '_traces__' + pop + '.png'
  )

# for pop_ind, pop in enumerate(plotPops):
#   rmpPops[pop] = np.mean(traces_dict['tracesData'][pop_ind]['cell_' + str(pop_ind) + '_V_soma'])

spikeFig, spikesDict = sim.analysis.plotSpikeStats()

newOUmap = {
    'OUamp': sim.cfg.OUamp,
    'OUvar': sim.cfg.OUvar
}
avgRates = sim.analysis.popAvgRates(tranges=[2000, 3000], show=False)

for idx, pop in enumerate(cfg.allpops):
  newOUmap[pop] = {}
  newOUmap[pop]['rate'] = avgRates[pop]
  newOUmap[pop]['isicv'] = np.mean(spikesDict['statData'][idx])


# append_to_json('../A1/simOutput/OUmapping.json', newOUmap)
# append_to_json('data/rmpPops.json', rmpPops)
# Terminate batch process
if comm.is_host():
  netParams.save("{}/{}_params.json".format(cfg.saveFolder, cfg.simLabel))
  print('transmitting data...')
  inputs = specs.get_mappings()
  results = sim.analysis.popAvgRates(tranges= [1000, 2000], show=False)
  # results['loss'] = results['TC']
  out_json = json.dumps({**inputs, **results})

  print(out_json)

  comm.send(out_json)
  comm.close()
#
# sim.close()
