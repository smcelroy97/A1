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
from netParams import netParams, cfg
import numpy as np
import matplotlib.pyplot as plt
from netpyne.analysis import spikes_legacy
from analysis.simTools import editNet

comm.initialize()

sim.initialize(simConfig = cfg,
               netParams = netParams)  		# create network object and set cfg and net params
sim.net.createPops()               			# instantiate network populations
sim.net.createCells()              			# instantiate network cells based on defined populations

editNet.setdminID(sim, cfg.allpops)
if cfg.cochlearThalInput: editNet.setCochCellLocationsX(sim, 'cochlea', netParams.popParams['cochlea']['numCells'], cfg.sizeX)

sim.net.connectCells()            			# create connections between cells based on params
sim.net.addStims() 							# add network stimulation
sim.setupRecording()              			# setup variables to record for each cell (spikes, V traces, etc)
sim.runSim()                                    # run parallel Neuron simulation
sim.saveDataInNodes()
sim.gatherDataFromFiles()

if comm.is_host():
  netParams.save("{}/{}_params.json".format(cfg.saveFolder, cfg.simLabel))
  print('transmitting data...')
  inputs = specs.get_mappings()
  results = sim.analysis.popAvgRates(show=False)

  results['TCRates'] = sim.analysis.popAvgRates(popName='TC', show=False)

sim.saveData()
sim.analysis.plotData()    # plot spike raster etc

comm.send(out_json)
comm.close()

# checking branch stability

# spikes_legacy.plotSpikeHist(include=['cochlea', 'TC'], timeRange=[0, 6000],
#                             saveFig=True)


