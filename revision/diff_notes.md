// ------------------------ ADD PARAM VALUES FROM .JSON FILES: 
// COMMENT THIS OUT IF USING GCP !!! ONLY USE IF USING NEUROSIM!!! 
with open('data/v34_batch25/trial_2142/trial_2142_cfg.json', 'rb') as f:
	cfgLoad = json.load(f)['simConfig']

- **cells/**
	- HTC_reduced_cellParams.json
		"cal": {"gcalbar": 0.001 -> 0.002}
		"htc": {"gmax": 1e-6 -> 1e-5}
		"ittc": {"gmax": 0.02 -> 0.2}
	- ITS4_reduced_cellParams.json
		"weightNorm": 0.000815 -> 0.001465
	- TC_reduced_cellParams.json
		"cal": {"gcalbar": None -> 0.002}
		"htc": {"gmax": 1e-6 -> 1e-5}
		"ittc": {"gmax": 0.02 -> 0.2}
	- sTC.py
		self.soma.gcalbar_cal = 0.00

- **cfg.json**
	- Gains
		- Removed
			BkgCtxEGain
			BkgCtxIGain
			CT6ScaleFactor
			CTGainThalI            
			L3L3scaleFactor
			L3L4PV
			L3L4SOM
			L4L4E
			NGF6bkgGain            
			intraThalamicEEGain
			intraThalamicEIGain
			intraThalamicIEGain
			intraThalamicIIGain
		- Changed
			EEGain
			IEGain
			EELayerGain
			EILayerGain
			IELayerGain   
			IILayerGain
			EICellTypeGain 
			IECellTypeGain
			EbkgThalamicGain
			IbkgThalamicGain  
			intraThalamicGain
			thalamoCorticalGain  
	- WeightFractions:
		- Removed
			synWeightFractionNGFE (replaced by cfg.synWeightFractionNGF)
			synWeightFractionNGFI
			synWeightFractionSOME (replaced by cfg.synWeightFractionSOM)
			synWeightFractionSOMI
			synWeightFractionThalCtxIE (replaced by dconf['syn']['synWeightFractionThal']['Ctx']['I'])
			synWeightFractionThalCtxII
			synWeightFractionThalIE (replaced by dconf['syn']['synWeightFractionThal']['Thal']['I'])
			synWeightFractionThalII
		- Changed
			- synWeightFractionSOM
				Old: {"synWeightFractionSOME": [0.9, 0.2], "synWeightFractionSOMI": [0.9, 0.1]}
				New: {"E": [0.9, 0.2], "I": 1}
	- AMPATau2Factor: 1
	- popParams['ITS4']['cellType']
		Old: ITS4
		New: IT
	- wmat
		IT2->PV2
		IT2->SOM2
		IT2->SOM3
		IT3->PV2
		IT3->SOM2
		IT3->SOM3
		PV2->PV2
		PV2->VIP2
		PV3->PV2
		PV3->VIP2
		SOM2->PV2
		SOM2->VIP2
		SOM3->PV2
		SOM3->VIP2
		VIP2->SOM2
		VIP2->SOM3
		VIP3->SOM2
		VIP3->SOM3

- **netParams** (not from cfg; directly from dconf=sim.json or hardcoded in sim.py)
	- Distance-dependent thalamic connectivity (lambda=50)
		Old: [TC, HTC]
		New: [TC, HTC, TI, IRE]
	- synMechParams
		- GABAB -> GABABCtx + GABABThal (just rename, params are the same)
			- GABABCtx for "SOM|NGF->..." conn and "SOM|NGF->E" subConn
			- GABABThal for "IThal->Thal"
		- synMechWeightFactor 
			- IThal->EThal 
				Old: [0.9, 0.2] (synWeightFractionThalIE)
				New: [0.9, 0.4] (from sim.json: dconf['syn']['synWeightFractionThal']['Thal']['I']['E'])
	- Gains
		- Thal->Thal
	!		From dconf['net']['intraThalamic(Core)(E|I)(E|I)Gain'] -- same as the one removed from cfg?



- **input.py** - use the new one?

