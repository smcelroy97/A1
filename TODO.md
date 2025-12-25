## TODO

### 1. Problem definition:

Solution    -> appropriate channel densities for relevant channels

Constraints -> depol block should happen at a reasonable I
            -> no multi-stability ( no multiple regimes) -> consolidate regions between  resting and depol ..
            -> validate across multiple input stimulus (internal loop)
                -> within solutions we shouldn't see 

#### 1a. define parameters:constraints for sweep
* channel densities?
  * preserve segment properties of PT cells (don't touch iH)
    * gbar kdr changed - not able to get a non-bistable f/i curve
    * no HH channels (no fast)
    * target bar <-
    * o/w no stricter guidance--
  * -> implement uniform ratio <- to start out look into distributions later 
  * search bounds


#### 1b. define analysis/fitness functions for sweep
* similarity to f/i curve? not as important
  * state transitions ( (rest->spiking) >>->block)
    * move depol block to earlier
    * frequency ceiling much lower
  * f(i) < (f'(i) similarities)
* bistability
  * mathematical characterization
  * thresholds for bistability tolerance --
* changing input stimulation (rx, wx, amp) should not produce a bistable curve

### 2. Python implementation: (grid search -> automated search)

#### 2a. implement parameter batch
* place parameters into cfg for batch 

#### 2b. implement analysis/fitness functions in NetPyNE
* through simulation data values

### 3. Analysis: (grid search -> automated search)

#### 3a. present findings for review

#### 3b. refactoring (2 or 1 as necessary)

## NOTES
### Implementation:

entrypoint: 
init.py?
desired outcome: 
sim_output/sim_IT5A_kdr_mult_1_ramp_1.5_rx_75_wx_0.5/fi_curve_IT5A.png
w/o bistability?
cell: 
IT5A_reduced ()

stimulation parameters also searchable?

collapse

stimulation is a constraint -->

various stimulation <-
### Timeline:
January -> set up software to perform parameter sweep w/ input sweep
(nested batches)

### Distribution:

### Additional:


