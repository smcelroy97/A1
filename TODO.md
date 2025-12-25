## TODO

### Meeting Notes

### 1. Problem definition:

Parameter Space:
* conductance for various channels s/t cell no longer exhibits undesired behavior
  * should avoid ih and any fast acting channels.
  * NOTE: altering slow channels will alter AP characteristics of the cell

Desired/Undesired behavior:
* unwanted: cell exhibits different fi curve "behaviors" (/multiple states) after a stimulus is applied
  * see cfg.py -> cfg.ou variables (tuning/cfg.py:73)
* unwanted: altering channel conductance can dramatically change fi curve including f(i) during spiking behavior & @ what (i) depol blockade occurs

Loss function: 3 objectives. 
* parameters which generate a cell with different fi curve "behaviors" (tuning/TODO.md:13) should have worse fitness. 
* parameters which generate a cell with different depolarization blockade thresholds should have worse fitness.
* parameters which generate a cell with different f(i) (NOTE: compared to what reference) should have worse fitness.

### 2. Python Implementation:
* search should be applied to any channel conductances as appropriate
* internally, for each parameter vector, fi curve should be sampled across a cfg.ou grid

### 3. Likely schedule (next steps for January):

* quickest solution given current code base -
  * outer search suggests a parameter vector to inner search
    * inner search performs a grid search across cfg.ou
0a. code initial small grid search for outer parameters and inner cfg.ou (January)
  * need to refactor to allow application of suggested parameter vector to the cell parameters (January)
  * need to code outer and inner grid search (January)
0b. decide & code loss function/metric recordings to be captured. (January?)
1.  review scores and plots of initial small grid search, validate that loss function/metric creates scores as desired, revisit 0b. as necessary
2.  migrate initial small grid search to a larger optimization function (CMA-ES/TSPE/NSGA2/...)

tuning/figures/notes0.png
