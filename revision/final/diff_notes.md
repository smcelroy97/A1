
- **cells/**
	- HTC_reduced_cellParams.json
		"cal": {"gcalbar": 0.001 -> 0.002}  (old -> new)
		"htc": {"gmax": 1e-6 -> 1e-5}
		"ittc": {"gmax": 0.02 -> 0.2}
	- ITS4_reduced_cellParams.json
		"weightNorm": 0.000815 -> 0.001465
	- TC_reduced_cellParams.json
		"cal": {"gcalbar": None -> 0.002}
		"htc": {"gmax": 1e-6 -> 1e-5}
		"ittc": {"gmax": 0.02 -> 0.2}
	- sTC.py
		self.soma.insert('cal')
    	self.soma.gcalbar_cal = 0.001

- **cfg**
	- Gains (auto diff., some values may stay the same, just renamed)
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
			EICellTypeGain  (from cfgLoad <- trial_2142_cfg.json)
			IECellTypeGain  (from cfgLoad <- trial_2142_cfg.json)
			EbkgThalamicGain
			IbkgThalamicGain  
			intraThalamicGain  (from cfgLoad <- trial_2142_cfg.json)
			thalamoCorticalGain  
	- synWeightFractionSOM
		Old: {"synWeightFractionSOME": [0.9, 0.2], "synWeightFractionSOMI": [0.9, 0.1]}
		New: {"E": [0.9, 0.2], "I": 1}
	- popParams['ITS4']['cellType']
		Old: ITS4
		New: IT
	- wmat  (from cfgLoad <- trial_2142_cfg.json)
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
	- Distance-dependent thalamic connectivity
		Old: [TC, HTC]
		New: [TC, HTC, TI, IRE]
	- synMechParams
		- synMechWeightFactor 
			- ThalI -> ThalE
				Old: [0.9, 0.2] (synWeightFractionThalIE)
				New: [0.9, 0.4] (from sim.json: dconf['syn']['synWeightFractionThal']['Thal']['I']['E'])
	- Gains (auto diff., some values may stay the same, just renamed)
		- Thal->Thal:  from dconf['net']['intraThalamic(Core)(E|I)(E|I)Gain']
