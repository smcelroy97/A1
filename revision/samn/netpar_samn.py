
Epops = ['IT2', 'IT3', 'ITP4', 'ITS4', 'IT5A', 'CT5A', 'IT5B', 'CT5B' , 'PT5B', 'IT6', 'CT6']  # all layers

Ipops = ['NGF1',                            # L1
        'PV2', 'SOM2', 'VIP2', 'NGF2',      # L2
        'PV3', 'SOM3', 'VIP3', 'NGF3',      # L3
        'PV4', 'SOM4', 'VIP4', 'NGF4',      # L4
        'PV5A', 'SOM5A', 'VIP5A', 'NGF5A',  # L5A  
        'PV5B', 'SOM5B', 'VIP5B', 'NGF5B',  # L5B
        'PV6', 'SOM6', 'VIP6', 'NGF6']      # L6 

Etypes = ['IT', 'ITS4', 'PT', 'CT']
Itypes = ['PV', 'SOM', 'VIP', 'NGF']

cfg = {}
netParams = {}

connData = {}
pmat = connData['pmat']
lmat = connData['lmat']
wmat = connData['wmat']
bins = connData['bins']
connDataSource = connData['connDataSource']

def wireCortex ():
  layerGainLabels = ['1', '2', '3', '4', '5A', '5B', '6']
  #------------------------------------------------------------------------------
  ## E -> E
  if cfg.EEGain > 0.0:
      for pre in Epops:
          for post in Epops:
              for l in layerGainLabels:  # used to tune each layer group independently
                  scaleFactor = 1.0
                  if connDataSource['E->E/I'] in ['Allen_V1', 'Allen_custom']:
                      prob = '%f * exp(-dist_2D/%f)' % (pmat[pre][post], lmat[pre][post])
                  else:
                      prob = pmat[pre][post]
                  if pre=='ITS4' or pre=='ITP4':
                      if post=='IT3':
                          scaleFactor = cfg.L4L3E  #25
                  netParams.connParams['EE_'+pre+'_'+post+'_'+l] = { 
                      'preConds': {'pop': pre}, 
                      'postConds': {'pop': post, 'ynorm': layer[l]},
                      'synMech': ESynMech,
                      'probability': prob,
                      'weight': wmat[pre][post] * cfg.EEGain * cfg.EELayerGain[l] * cfg.EEPopGain[post] * scaleFactor, 
                      'synMechWeightFactor': cfg.synWeightFractionEE,
                      'delay': 'defaultDelay+dist_3D/propVelocity',
                      'synsPerConn': 1,
                      'sec': 'dend_all'}                    
  #------------------------------------------------------------------------------
  ## E -> I       ## MODIFIED FOR NMDAR MANIPULATION!! 
  if cfg.EIGain > 0.0:
      for pre in Epops:
          for post in Ipops:
              for postType in Itypes:
                  if postType in post: # only create rule if celltype matches pop
                      for l in layerGainLabels:  # used to tune each layer group independently
                          scaleFactor = 1.0
                          if connDataSource['E->E/I'] in ['Allen_V1', 'Allen_custom']:
                              prob = '%f * exp(-dist_2D/%f)' % (pmat[pre][post], lmat[pre][post])
                          else:
                              prob = pmat[pre][post]                        
                          if 'NGF' in post:
                              synWeightFactor = cfg.synWeightFractionENGF   
                          elif 'PV' in post:
                              synWeightFactor = cfg.synWeightFractionEI_CustomCort
                          else:
                              synWeightFactor = cfg.synWeightFractionEI #cfg.synWeightFractionEI_CustomCort  #cfg.synWeightFractionEI   
                          if 'NGF1' in post:
                              scaleFactor = cfg.ENGF1  
                          if pre=='ITS4' or pre=='ITP4':
                              if post=='PV3':
                                  scaleFactor = cfg.L4L3PV#25
                              elif post=='SOM3':
                                  scaleFactor = cfg.L4L3SOM
                              elif post=='NGF3':
                                  scaleFactor = cfg.L4L3NGF#25
                              elif post=='VIP3':
                                  scaleFactor = cfg.L4L3VIP#25
                          netParams.connParams['EI_'+pre+'_'+post+'_'+postType+'_'+l] = { 
                              'preConds': {'pop': pre}, 
                              'postConds': {'pop': post, 'cellType': postType, 'ynorm': layer[l]},
                              'synMech': ESynMech,
                              'probability': prob,
                              'weight': wmat[pre][post] * cfg.EIGain * cfg.EICellTypeGain[postType] * cfg.EILayerGain[l] * cfg.EIPopGain[post] * scaleFactor, 
                              'synMechWeightFactor': synWeightFactor,
                              'delay': 'defaultDelay+dist_3D/propVelocity',
                              'synsPerConn': 1,
                              'sec': 'proximal'}                
  # cfg.NMDARfactor * wmat[pre][post] * cfg.EIGain * cfg.EICellTypeGain[postType] * cfg.EILayerGain[l]]
  #------------------------------------------------------------------------------
  ## I -> E
  if cfg.IEGain > 0.0:
      if connDataSource['I->E/I'] == 'Allen_custom':
          for pre in Ipops:
              for preType in Itypes:
                  if preType in pre:  # only create rule if celltype matches pop
                      for post in Epops:
                          for l in layerGainLabels:  # used to tune each layer group independently                            
                              prob = '%f * exp(-dist_2D/%f)' % (pmat[pre][post], lmat[pre][post])
                              synWeightFactor = cfg.synWeightFractionIE
                              if 'SOM' in pre:
                                  synMech = SOMESynMech
                                  synWeightFactor = cfg.synWeightFractionSOM['E']
                              elif 'PV' in pre:
                                  synMech = PVSynMech
                              elif 'VIP' in pre:
                                  synMech = VIPSynMech
                              elif 'NGF' in pre:
                                  synMech = NGFESynMech
                                  synWeightFactor = cfg.synWeightFractionNGF['E']
                              netParams.connParams['IE_'+pre+'_'+preType+'_'+post+'_'+l] = { 
                                  'preConds': {'pop': pre}, 
                                  'postConds': {'pop': post, 'ynorm': layer[l]},
                                  'synMech': synMech,
                                  'probability': prob,
                                  'weight': wmat[pre][post] * cfg.IEGain * cfg.IECellTypeGain[preType] * cfg.IELayerGain[l], 
                                  'synMechWeightFactor': synWeightFactor,
                                  'delay': 'defaultDelay+dist_3D/propVelocity',
                                  'synsPerConn': 1,
                                  'sec': 'proximal'}                    
  #------------------------------------------------------------------------------
  ## I -> I
  if cfg.IIGain > 0.0:
      if connDataSource['I->E/I'] == 'Allen_custom':
          for pre in Ipops:
              for post in Ipops:
                  for l in layerGainLabels:                     
                      prob = '%f * exp(-dist_2D/%f)' % (pmat[pre][post], lmat[pre][post])
                      synWeightFactor = cfg.synWeightFractionII
                      if 'SOM' in pre:
                          synMech = SOMISynMech
                          synWeightFactor = cfg.synWeightFractionSOM['I']
                      elif 'PV' in pre:
                          synMech = PVSynMech
                      elif 'VIP' in pre:
                          synMech = VIPSynMech
                      elif 'NGF' in pre:
                          synMech = NGFISynMech
                          synWeightFactor = cfg.synWeightFractionNGF['I']                          
                      netParams.connParams['II_'+pre+'_'+post+'_'+l] = { 
                          'preConds': {'pop': pre}, 
                          'postConds': {'pop': post,  'ynorm': layer[l]},
                          'synMech': synMech,
                          'probability': prob,
                          'weight': wmat[pre][post] * cfg.IIGain * cfg.IILayerGain[l], 
                          'synMechWeightFactor': synWeightFactor,
                          'delay': 'defaultDelay+dist_3D/propVelocity',
                          'synsPerConn': 1,
                          'sec': 'proximal'}                        


def IsThalamicCore (ct):
    return ct == 'TC' or ct == 'HTC' or ct == 'IRE' or ct == 'TI'

def wireThal ():
    
  # set intrathalamic connections
  for pre in TEpops+TIpops:
      for post in TEpops+TIpops:
          gain = cfg.intraThalamicGain
          if post in pmat[pre]:
              # for syns use ESynMech, ThalIESynMech and ThalIISynMech
              if pre in TEpops:     # E->E/I
                  syn = ESynMech
                  synWeightFactor = cfg.synWeightFractionEE
                  if post in TEpops:
                    if IsThalamicCore(pre) and IsThalamicCore(post):                      
                      gain *= dconf['net']['intraThalamicCoreEEGain']
                    else:
                      gain *= dconf['net']['intraThalamicEEGain']
                  else:
                    if IsThalamicCore(pre) and IsThalamicCore(post):                      
                      gain *= dconf['net']['intraThalamicCoreEIGain']
                    else:
                      gain *= dconf['net']['intraThalamicEIGain']
              elif post in TEpops:  # I->E
                  syn = ThalIESynMech
                  synWeightFactor = dconf['syn']['synWeightFractionThal']['Thal']['I']['E']
                  if IsThalamicCore(pre) and IsThalamicCore(post):                                        
                    gain *= dconf['net']['intraThalamicCoreIEGain']
                  else:
                    gain *= dconf['net']['intraThalamicIEGain']
              else:                  # I->I
                  syn = ThalIISynMech
                  synWeightFactor = dconf['syn']['synWeightFractionThal']['Thal']['I']['I']
                  if IsThalamicCore(pre) and IsThalamicCore(post):
                    gain *= dconf['net']['intraThalamicCoreIIGain']
                  else:
                    gain *= dconf['net']['intraThalamicIIGain']
              # use spatially dependent wiring between thalamic core excitatory neurons
              #if (pre == 'TC' and (post == 'TC' or post == 'HTC')) or (pre == 'HTC' and (post == 'TC' or post == 'HTC')):
              #  prob = '%f * exp(-dist_x/%f)' % (pmat[pre][post], dconf['net']['ThalamicCoreLambda'])
              # use spatially dependent wiring between thalamic core neurons
              if IsThalamicCore(pre) and IsThalamicCore(post):
                prob = '%f * exp(-dist_x/%f)' % (pmat[pre][post], dconf['net']['ThalamicCoreLambda'])
              else:
                prob = pmat[pre][post]
              # print('wireThal:',pre,post)
              netParams.connParams['ITh_'+pre+'_'+post] = { 
                  'preConds': {'pop': pre}, 
                  'postConds': {'pop': post},
                  'synMech': syn,
                  'probability': prob,
                  'weight': wmat[pre][post] * gain,
                  'synMechWeightFactor': synWeightFactor,
                  'delay': 'defaultDelay+dist_3D/propVelocity',
                  'synsPerConn': 1,
                  'sec': 'soma'}


#-----------------------------------------------------------------------------
def connectCortexToThal ():
  # corticothalamic connections
  for pre in Epops:
      for post in TEpops+TIpops:
          if post in pmat[pre]:
              if IsThalamicCore(post): # use spatially dependent wiring for thalamic core
                prob = '%f * exp(-dist_x/%f)' % (pmat[pre][post], dconf['net']['ThalamicCoreLambda'])
              else:
                prob = pmat[pre][post]              
              netParams.connParams['CxTh_'+pre+'_'+post] = { 
                  'preConds': {'pop': pre}, 
                  'postConds': {'pop': post},
                  'synMech': ESynMech,
                  'probability': prob,
                  'weight': wmat[pre][post] * cfg.corticoThalamicGain, 
                  'synMechWeightFactor': cfg.synWeightFractionEE,
                  'delay': 'defaultDelay+dist_3D/propVelocity',
                  'synsPerConn': 1,
                  'sec': 'soma'}

if cfg.addConn and cfg.addCorticoThalamicConn: connectCortexToThal()              

#------------------------------------------------------------------------------
def connectThalToCortex ():
  # thalamocortical connections, some params added from Christoph Metzner's branch
  for pre in TEpops+TIpops:
      for post in Epops+Ipops:
          scaleFactor = 1.0
          if post in pmat[pre]:
              if IsThalamicCore(pre): # use spatially dependent wiring for thalamic core
                prob = '%f * exp(-dist_x/%f)' % (pmat[pre][post], dconf['net']['ThalamicCoreLambda']) # NB: should check if this is ok 
              else:
                prob = '%f * exp(-dist_2D/%f)' % (pmat[pre][post], lmat[pre][post]) # NB: check what the 2D inverse distance based on. lmat from conn/conn.pkl
              # for syns use ESynMech, SOMESynMech and SOMISynMech 
              if pre in TEpops:     # E->E/I
                  if post=='PV4':
                      syn = ESynMech
                      synWeightFactor = cfg.synWeightFractionEE
                      scaleFactor = cfg.thalL4PV#25
                  elif post=='SOM4':
                      syn = ESynMech
                      synWeightFactor = cfg.synWeightFractionEE
                      scaleFactor = cfg.thalL4SOM
                  elif post=='ITS4':
                      syn = ESynMech
                      synWeightFactor = cfg.synWeightFractionEE
                      scaleFactor = cfg.thalL4E#25
                  elif post=='ITP4':
                      syn = ESynMech
                      synWeightFactor = cfg.synWeightFractionEE
                      scaleFactor = cfg.thalL4E#25
                  elif post=='NGF4':
                      syn = ESynMech
                      synWeightFactor = cfg.synWeightFractionEE
                      scaleFactor = cfg.thalL4NGF#25
                  elif post=='VIP4':
                      syn = ESynMech
                      synWeightFactor = cfg.synWeightFractionEE
                      scaleFactor = cfg.thalL4VIP#25
                  elif post=='NGF1':
                      syn = ESynMech
                      synWeightFactor = cfg.synWeightFractionEE
                      scaleFactor = cfg.thalL1NGF#25
                  else:
                      syn = ESynMech
                      synWeightFactor = cfg.synWeightFractionEE
              elif post in Epops:  # I->E
                  syn = ThalIESynMech
                  synWeightFactor = cfg.synWeightFractionThal['Ctx']['I']['E']
              else:                  # I->I
                  syn = ThalIISynMech
                  synWeightFactor = fg.synWeightFractionThal['Ctx']['I']['I']
              # print('thal->ctx ', pre, post)
              netParams.connParams['ThCx_'+pre+'_'+post] = { 
                  'preConds': {'pop': pre}, 
                  'postConds': {'pop': post},
                  'synMech': syn,
                  'probability': prob,
                  'weight': wmat[pre][post] * cfg.thalamoCorticalGain * scaleFactor, 
                  'synMechWeightFactor': synWeightFactor,
                  'delay': 'defaultDelay+dist_3D/propVelocity',
                  'synsPerConn': 1,
                  'sec': 'soma'}                  

if cfg.addConn and cfg.addThalamoCorticalConn: connectThalToCortex()
              
#------------------------------------------------------------------------------
# Subcellular connectivity (synaptic distributions)
#------------------------------------------------------------------------------  
# Set target sections (somatodendritic distribution of synapses)
# From Billeh 2019 (Allen V1) (fig 4F) and Tremblay 2016 (fig 3)
def addSubConn ():
  #------------------------------------------------------------------------------
  # E -> E2/3,4: soma,dendrites <200um
  netParams.subConnParams['E->E2,3,4'] = {
      'preConds': {'cellType': ['IT', 'ITS4', 'PT', 'CT']}, 
      'postConds': {'pops': ['IT2', 'IT3', 'ITP4', 'ITS4']},
      'sec': 'proximal',
      'groupSynMechs': ESynMech, 
      'density': 'uniform'} 
  #------------------------------------------------------------------------------
  # E -> E5,6: soma,dendrites (all)
  netParams.subConnParams['E->E5,6'] = {
      'preConds': {'cellType': ['IT', 'ITS4', 'PT', 'CT']}, 
      'postConds': {'pops': ['IT5A', 'CT5A', 'IT5B', 'PT5B', 'CT5B', 'IT6', 'CT6']},
      'sec': 'all',
      'groupSynMechs': ESynMech, 
      'density': 'uniform'}
  #------------------------------------------------------------------------------
  # E -> I: soma, dendrite (all)
  netParams.subConnParams['E->I'] = {
      'preConds': {'cellType': ['IT', 'ITS4', 'PT', 'CT']}, 
      'postConds': {'cellType': ['PV','SOM','NGF', 'VIP']},
      'sec': 'all',
      'groupSynMechs': ESynMech, 
      'density': 'uniform'} 
  #------------------------------------------------------------------------------
  # NGF1 -> E: apic_tuft
  netParams.subConnParams['NGF1->E'] = {
      'preConds': {'pops': ['NGF1']}, 
      'postConds': {'cellType': ['IT', 'ITS4', 'PT', 'CT']},
      'sec': 'apic_tuft',
      'groupSynMechs': NGFESynMech, 
      'density': 'uniform'} 
  #------------------------------------------------------------------------------
  # NGF2,3,4 -> E2,3,4: apic_trunk
  netParams.subConnParams['NGF2,3,4->E2,3,4'] = {
      'preConds': {'pops': ['NGF2', 'NGF3', 'NGF4']}, 
      'postConds': {'pops': ['IT2', 'IT3', 'ITP4', 'ITS4']},
      'sec': 'apic_trunk',
      'groupSynMechs': NGFESynMech, 
      'density': 'uniform'} 
  #------------------------------------------------------------------------------
  # NGF2,3,4 -> E5,6: apic_uppertrunk
  netParams.subConnParams['NGF2,3,4->E5,6'] = {
      'preConds': {'pops': ['NGF2', 'NGF3', 'NGF4']}, 
      'postConds': {'pops': ['IT5A', 'CT5A', 'IT5B', 'PT5B', 'CT5B', 'IT6', 'CT6']},
      'sec': 'apic_uppertrunk',
      'groupSynMechs': NGFESynMech, 
      'density': 'uniform'} 
  #------------------------------------------------------------------------------
  # NGF5,6 -> E5,6: apic_lowerrunk
  netParams.subConnParams['NGF5,6->E5,6'] = {
      'preConds': {'pops': ['NGF5A', 'NGF5B', 'NGF6']}, 
      'postConds': {'pops': ['IT5A', 'CT5A', 'IT5B', 'PT5B', 'CT5B', 'IT6', 'CT6']},
      'sec': 'apic_lowertrunk',
      'groupSynMechs': NGFESynMech, 
      'density': 'uniform'} 
  #------------------------------------------------------------------------------
  #  SOM -> E: all_dend (not close to soma)
  netParams.subConnParams['SOM->E'] = {
      'preConds': {'cellType': ['SOM']}, 
      'postConds': {'cellType': ['IT', 'ITS4', 'PT', 'CT']},
      'sec': 'dend_all',
      'groupSynMechs': SOMESynMech, 
      'density': 'uniform'} 
  #------------------------------------------------------------------------------
  #  PV -> E: proximal
  netParams.subConnParams['PV->E'] = {
      'preConds': {'cellType': ['PV']}, 
      'postConds': {'cellType': ['IT', 'ITS4', 'PT', 'CT']},
      'sec': 'proximal',
      'groupSynMechs': PVSynMech, 
      'density': 'uniform'} 
  #------------------------------------------------------------------------------
  #  TC -> E: proximal
  netParams.subConnParams['TC->E'] = {
      'preConds': {'cellType': ['TC', 'HTC']}, 
      'postConds': {'cellType': ['IT', 'ITS4', 'PT', 'CT']},
      'sec': 'proximal',
      'groupSynMechs': ESynMech, 
      'density': 'uniform'} 
  #------------------------------------------------------------------------------
  #  TCM -> E: apical
  netParams.subConnParams['TCM->E'] = {
      'preConds': {'cellType': ['TCM']}, 
      'postConds': {'cellType': ['IT', 'ITS4', 'PT', 'CT']},
      'sec': 'apic',
      'groupSynMechs': ESynMech, 
      'density': 'uniform'}

if cfg.addSubConn: addSubConn()  

