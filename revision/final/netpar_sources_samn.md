
Sources of the parameters that affect netParams but not included into cfg.

- **dconf (sim.json)**
    - synMechParams
        - netParams.synMechParams['GABABThal'] = dconf['syn']['GABABThal']
        - netParams.synMechParams['GABABCtx'] = dconf['syn']['GABABCtx']
    - synMechWeightFactor
        - ThalI -> Thal:  dconf['syn']['synWeightFractionThal']['Thal']['I']['E|I']
    - Gains:
        - Thal->Thal:  dconf['net']['intraThalamic(Core)(E|I)(E|I)Gain']
    - Distance exponents:
        - ThalCore <-> ThalCore:  dconf['net']['ThalamicCoreLambda'])
        - ThalCore <-> Cortex:  dconf['net']['ThalamicCoreLambda'])
