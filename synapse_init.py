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
from CurrentStim import CurrentStim as CS
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

#########################################################################################
# - Adding OU Nose Stims for each Cell
#########################################################################################

if sim.cfg.addNoiseIClamp:
  sim, vecs_dict = CS.addNoiseIClamp(sim)

sim.setupRecording()              			# setup variables to record for each cell (spikes, V traces, etc)
sim.runSim()                                    # run parallel Neuron simulation
sim.saveDataInNodes()
sim.gatherDataFromFiles()
sim.saveData()
sim.analysis.plotData()    # plot spike raster etc

trace_analysis = {}

plotPops = []
for cell in sim.net.cells:
    for conn in cell.conns:
        if conn['weight'] >0:
            if cell.tags['pop'] not in plotPops:
                plotPops.append(cell.tags['pop'])

try:
  record_pops = [(pop, list(np.arange(0, netParams.popParams[pop]['numCells']))) for pop in plotPops]
except:
  record_pops = [(pop, list(np.arange(0, 40))) for pop in plotPops]

for pop_ind, pop in enumerate(plotPops):
  print('\n\n', pop)
  # sim.analysis.plotTraces(
  figs, traces_dict = sim.analysis.plotTraces(
    include=[pop],
    # include=[record_pops[pop_ind]],
    timeRange=[100, 200],
    overlay=True, oneFigPer='trace',
    ylim=[-90, -40],
    axis=True,
    # figSize=(70, 15),
    figSize=(25, 15),
    # figSize=(60, 18),
    fontSize=15,
    # saveFig=True,
    # saveFig=sim.cfg.saveFigPath+'/'+sim.cfg.filename+'_traces_'+pop+ '.png',
    saveFig=sim.cfg.saveFolder + '/' + sim.cfg.simLabel + '_traces__' + pop + '.png',
  )
  for item in traces_dict['tracesData'][0]:
    if 'soma' in item:
      trace_analysis[pop] = traces_dict['tracesData'][0][item]

basemV = {}
amp = {}
peak = {}

for pop in trace_analysis:
    basemV[pop] = trace_analysis[pop][0]
    abs_trace = [abs(i) for i in trace_analysis[pop]]
    peak_idx = np.array(abs_trace).argmax()
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
  results['loss'] = dummy[0]/3
  out_json = json.dumps({**inputs, **results})

  print(out_json)

  comm.send(out_json)
  comm.close()

sim.close()
