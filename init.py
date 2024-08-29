"""
init.py

Starting script to run NetPyNE-based A1 model.


Usage:
    python init.py # Run simulation, optionally plot a raster


MPI usage:
    mpiexec -n 4 nrniv -python -mpi init.py


Contributors: ericaygriffith@gmail.com, salvadordura@gmail.com
"""
import matplotlib; matplotlib.use('Agg')  # to avoid graphics error in servers
from input import cochlearInputSpikes
from netpyne import sim
import numpy as np
import matplotlib.pyplot as plt
from netpyne.analysis import spikes_legacy


cfg, netParams = sim.readCmdLineArgs(simConfigDefault='cfg.py', netParamsDefault='netParams.py')

sim.initialize(simConfig = cfg,
               netParams = netParams)  		# create network object and set cfg and net params
sim.net.createPops()               			# instantiate network populations
sim.net.createCells()              			# instantiate network cells based on defined populations

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

if cfg.cochlearThalInput: setCochCellLocationsX('cochlea', netParams.popParams['cochlea']['numCells'], cfg.sizeX)


sim.net.connectCells()            			# create connections between cells based on params

def checkCochConns():
  cochGids = []
  cochConns = []

  for cell in sim.net.cells:
    if cell.tags['pop'] == 'cochlea':
      cochGids.append(cell.gid)
  print('Number of Cochlea Cells is ' + str(len(cochGids)))

  for cell in sim.net.cells:
    if cell.tags['pop'] :
      for conn in cell.conns:
        if conn['preGid'] in cochGids:
          cochConns.append(conn)
          print(len(cochConns))
  print ('Number of Cochlea Conns is ' + str(len(cochConns)))

def checkTCconnRatio():
  TCConns = []
  L6TCConns = []
  IRETCConns = []
  CochTCConns = []
  for cell in sim.net.cells:
    if cell.tags['pop'] == 'TC':
      for conn in cell.conns:
        TCConns.append(conn['preGid'])
  for conn in TCConns:
      if conn in sim.net.pops['CT6'].cellGids:
          L6TCConns.append(conn)
      elif conn in sim.net.pops['IRE'].cellGids:
          IRETCConns.append(conn)
      elif conn in sim.net.pops['cochlea'].cellGids:
          CochTCConns.append(conn)
  pctCoch = (len(CochTCConns)/len(TCConns)) * 100
  pctIRE = (len(IRETCConns)/len(TCConns)) * 100
  pctL6 = (len(L6TCConns)/len(TCConns)) * 100

  print(str(pctCoch) + '% of TC Conns are from Cochlea')
  print(str(pctIRE) + '% of TC Conns are from IRE')
  print(str(pctL6) + '% of TC Conns are from CT6')



# checkCochConns()

sim.net.addStims() 							# add network stimulation
sim.setupRecording()              			# setup variables to record for each cell (spikes, V traces, etc)
sim.runSim()                                    # run parallel Neuron simulation
# sim.gatherData()                  			# gather spiking data and cell info from each node
sim.saveDataInNodes()
sim.gatherDataFromFiles()
# checkTCconnRatio()
# plotPops = ['TC', 'IRE']
# try:
#   record_pops = [(pop, list(np.arange(0, netParams.popParams[pop]['numCells']))) for pop in plotPops]
# except:
#   record_pops = [(pop, list(np.arange(0, 40))) for pop in plotPops]
#
# for pop_ind, pop in enumerate(plotPops):
#   print('\n\n', pop)
#   # sim.analysis.plotTraces(
#   figs, traces_dict = sim.analysis.plotTraces(
#     include=[pop],
#     # include=[record_pops[pop_ind]],
#     # timeRange=[490,550],
#     overlay=True, oneFigPer='trace',
#     ylim=[-110, 50],
#     axis=True,
#     figSize=(70, 15),
#     # figSize=(40, 15),
#     # figSize=(60, 18),
#     fontSize=15,
#     # saveFig=True,
#     # saveFig=sim.cfg.saveFigPath+'/'+sim.cfg.filename+'_traces_'+pop+ '.png',
#     saveFig=sim.cfg.saveFolder + '/' + sim.cfg.simLabel + '_traces__' + pop + '.png',
#   )
#
#   tracesData = traces_dict['tracesData']
#   # store_v={}
#   store_v = []
#   store_voltages = {}
#   for rec_ind in range(len(tracesData)):
#     for trace in tracesData[rec_ind].keys():
#       if '_V_soma' in trace:
#         cell_gid_str = trace.split('_V_soma')[0].split('cell_')[1]
#         # store_v.update({cell_gid_str:list(tracesData[rec_ind][trace])})
#         store_v.append(list(tracesData[rec_ind][trace]))
#         store_voltages.update({cell_gid_str: list(tracesData[rec_ind][trace])})
#
#   t_vector = list(tracesData[0]['t'])
#   mean_v = np.mean(store_v, axis=0)
#   t_vector_ = [t_vector[i] for i in range(len(mean_v))]
#   plt.figure(figsize=(70, 15))
#   for trace in store_v: plt.plot(t_vector_, trace, 'gray', alpha=0.2)
#   plt.plot(t_vector_, mean_v, 'r')
#   plt.ylim([-110, 50])
#   plt.xlim([min(t_vector_), max(t_vector_)])
#   # plt.plot(mean_v,'k')
#   plt.savefig(sim.cfg.saveFolder + '/' + sim.cfg.simLabel + '_mean_traces__' + pop + '.png')

sim.saveData()
sim.analysis.plotData()    # plot spike raster etc

# spikes_legacy.plotSpikeHist(include=['cochlea', 'TC'], timeRange=[0, 6000],
#                             saveFig=True)


