
Sources of the parameters included into cfg.

- **dconf (sim.json)**
    - Syn
        synWeightFractionEE
        synWeightFractionEI
        synWeightFractionIE
        synWeightFractionII
        synWeightFractionEI_CustomCort
        synWeightFractionNGF
        synWeightFractionSOM
        synWeightFractionENGF
    - Gains
        - Cortex
            EEGain
            EIGain
            IEGain
            IIGain
            EELayerGain
            EILayerGain
            IELayerGain        
            IILayerGain
            EEPopGain
            EIPopGain
            ENGF1
            L4L3E
            L4L3PV
            L4L3SOM
            L4L3VIP
            L4L3NGF
        - Thalamus
            EbkgThalamicGain
            IbkgThalamicGain
            corticoThalamicGain
            thalL1NGF
            thalL4E
            thalL4NGF
            thalL4PV
            thalL4SOM
            thalL4VIP
    - IC    
        ICThalInput
        ICThalMatrixCoreFactor
        ICThalprobECore
        ICThalprobICore
        ICThalweightECore
        ICThalweightICore
    - Flags    
        addIntraThalamicConn
        addCorticoThalamicConn
        addThalamoCorticalConn
        addIClamp
        addRIClamp
        addNetStim
    - Cochlea
        cochThalweightECore
        cochThalweightICore
        cochThalweightEMatrix
        cochThalweightIMatrix
        cochThalprobECore
        cochThalprobICore
        cochThalprobEMatrix
        cochThalprobIMatrix
        cochThalFreqRange
    - Geometry
        scale
        scaleDensity
        sizeX
        sizeY
        sizeZ
    

- **cfgLoad (data/v34_batch25/trial_2142/trial_2142_cfg.json)**
    - Gains
        intraThalamicGain 
        EICellTypeGain
        IECellTypeGain
        - Replaced from dconf
            EEGain
            EIGain
            IEGain
            IIGain
            EELayerGain
            EILayerGain
            IELayerGain
            IILayerGain
            EbkgThalamicGain
            IbkgThalamicGain
            thalamoCorticalGain
    - wmat

- **sim.py (hardcoded)**
    - Syn
        weightNormThreshold
        weightNormScaling
        AMPATau2Factor
    - Chan
        ihGbar
        KgbarFactor
    - Gains
        - Replaced from cfgLoad
            EICellTypeGain
            IECellTypeGain
        - Replaced from dconf
            EELayerGain
            EILayerGain
            IELayerGain
            IILayerGain        
    - IC
        ICThalInput
        ICThalprobEMatrix
        ICThalprobIMatrix
    - Flags
        addConn
        addBkgConn
        addSubConn
        removeWeightNorm
        useHScale
    - Bkg
        delayBkg
        noiseBkg
        rateBkg
        startBkg
    - Other
        tune
    - Replaced from cfgLoad:
        - wmat (conn/conn.pkl)