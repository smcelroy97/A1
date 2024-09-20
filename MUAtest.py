import numpy as np

def ms2index(ms, sampr): return int(sampr * ms / 1e3)

def drawstimhistCoch (simConfig,binsz=25):
  lcf = simConfig['simConfig']['cochlearCenterFreqs']
  frng = [750, 1250]
  minidx,maxidx = 1e9,-1e9
  for idx,f in enumerate(lcf):
    if f >= frng[0] and f <= frng[1]:
      minidx = min(minidx,idx)
      maxidx = max(maxidx,idx)
  minidx,maxidx # (2800, 3799) # 1000 total for core
  print('cochleaC',minidx,maxidx,maxidx-minidx+1)
  sh = {k:getspikehist(dspkT[k], dnumc[k], binsz, totalDur) for k in dnumc.keys()}
  lidx = [minidx+dstartidx['cochlea'],maxidx+dstartidx['cochlea']] # cochlear cells projecting to thalamic core
  sh['cochleaC'] = getspikehist(dspkT['cochlea'],maxidx-minidx+1,25,totalDur,lidx=lidx,spkID=dspkID['cochlea'])
  drawstimhist(sh,llk = [ ['cochlea','cochleaC'], ['TC', 'HTC', 'TCM'], ['IRE', 'IREM','TI','TIM'], ['ITP4', 'ITS4'], ['IT2', 'IT3'] ])
  return sh

def drawMUASSA (sh,
                lpop = ['TC'],\
                loffset = [0, 0, 0, 0, 0, 0, 0, 0, 0,],\
                llpop = [['TC','HTC']],\
                llclr = [['c','m']],sidx=0, bbnT =[2000, 2724, 3448, 4172, 4896, 5620, 6344]):
  dt = 25; sampr = 40
  bbnTrigIdx = [ms2index(x,sampr) for x in bbnT]
  MUAAmp = {pop:[np.mean(sh[pop][1][x+offset:x+offset+4]) for x in bbnTrigIdx] for pop,offset in zip(lpop,loffset)}

  gdx=1
  for lpop,lclr in zip (llpop,llclr):
    subplot(1,3,gdx)
    for pop,clr in zip(lpop,lclr):
      plot(MUAAmp[pop],clr); plot(MUAAmp[pop],clr+'o')
    gdx+=1
    lpatch = [mpatches.Patch(color=c,label=s) for c,s in zip(lclr,lpop)]
    gca().legend(handles=lpatch,handlelength=1)
    ylabel('MUA Freq (Hz)'); xlabel('Stim Number')
  return MUAAmp


from netpyne import sim

sim.initialize()
all = sim.loadAll('/Users/scoot/A1ProjData/A1_sim_data/TCnoCT0912/TCnoCT0912_00000_data.pkl')

drawMUASSA(sim.net.pops)