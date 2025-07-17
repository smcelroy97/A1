"""
init.py

Starting script to run NetPyNE-based A1 model.


Usage:
    python init.py # Run simulation, optionally plot a raster


MPI usage:
    mpiexec -n 4 nrniv -python -mpi init.py


Contributors: @gmail.com
"""

from netpyne.batchtools import specs, comm
import matplotlib; matplotlib.use('Agg')  # to avoid graphics error in servers
from matplotlib import pyplot as plt
from netpyne import sim
from netParams import netParams, cfg
import numpy as np
import json
import os

# cfg, netParams = sim.readCmdLineArgs(simConfigDefault='cfg.py', netParamsDefault='netParams.py')

cfg, netParams = sim.readCmdLineArgs()

sim.initialize(
    simConfig = cfg,
    netParams = netParams)  				# create network object and set cfg and net params
sim.net.createPops()               			# instantiate network populations
sim.net.createCells()              			# instantiate network cells based on defined populations
sim.net.connectCells()            			# create connections between cells based on params
sim.net.addStims() 							# add network stimulation
sim.setupRecording()              			# setup variables to record for each cell (spikes, V traces, etc)
sim.runSim()                      			# run parallel Neuron simulation
sim.gatherData()                  			# gather spiking data and cell info from each node
sim.saveData()                    			# save params, cell info and sim output to file (pickle,mat,txt,etc)#
sim.analysis.plotData()         			# plot spike raster etc

sim.analysis.plotTraces(oneFigPer='trace', overlay=False, timeRange=[1000,5000],axis=False,legend=False, showFig=False, subtitles=None, ylim= [-90,20], saveFig=True,
                        scaleBarLoc=1,figSize=(24, 15),fontSize=6);

Firing = sim.analysis.calculateRate(timeRange=[1000,5000])
print("FR = {}")
for i, pop in enumerate(Firing[0]):
    if i > 0: # and Firing[1][i] < 0.25
        print("FR['%s'] = %.2f" % (pop, Firing[1][i]))
