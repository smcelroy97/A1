: $Id: gabab.mod,v 1.9 2004/06/17 16:04:05 billl Exp $

COMMENT
-----------------------------------------------------------------------------

	Kinetic model of GABA-B receptors
	=================================

  MODEL OF SECOND-ORDER G-PROTEIN TRANSDUCTION AND FAST K+ OPENING
  WITH COOPERATIVITY OF G-PROTEIN BINDING TO K+ CHANNEL

  PULSE OF TRANSMITTER

  SIMPLE KINETICS WITH NO DESENSITIZATION

	Features:

  	  - peak at 100 ms; time course fit to Tom Otis' PSC
	  - SUMMATION (psc is much stronger with bursts)


	Approximations:

	  - single binding site on receptor
	  - model of alpha G-protein activation (direct) of K+ channel
	  - G-protein dynamics is second-order; simplified as follows:
		- saturating receptor
		- no desensitization
		- Michaelis-Menten of receptor for G-protein production
		- "resting" G-protein is in excess
		- Quasi-stat of intermediate enzymatic forms
	  - binding on K+ channel is fast


	Kinetic Equations:

	  dR/dt = K1 * T * (1-R-D) - K2 * R

	  dG/dt = K3 * R - K4 * G

	  R : activated receptor
	  T : transmitter
	  G : activated G-protein
	  K1,K2,K3,K4 = kinetic rate cst

  n activated G-protein bind to a K+ channel:

	n G + C <-> O		(Alpha,Beta)

  If the binding is fast, the fraction of open channels is given by:

	O = G^n / ( G^n + KD )

  where KD = Beta / Alpha is the dissociation constant

-----------------------------------------------------------------------------

  Parameters estimated from patch clamp recordings of GABAB PSP's in
  rat hippocampal slices (Otis et al, J. Physiol. 463: 391-407, 1993).

-----------------------------------------------------------------------------

  PULSE MECHANISM

  Kinetic synapse with release mechanism as a pulse.

  Warning: for this mechanism to be equivalent to the model with diffusion
  of transmitter, small pulses must be used...

  For a detailed model of GABAB:

  Destexhe, A. and Sejnowski, T.J.  G-protein activation kinetics and
  spill-over of GABA may account for differences between inhibitory responses
  in the hippocampus and thalamus.  Proc. Natl. Acad. Sci. USA  92:
  9515-9519, 1995.

  For a review of models of synaptic currents:

  Destexhe, A., Mainen, Z.F. and Sejnowski, T.J.  Kinetic models of
  synaptic transmission.  In: Methods in Neuronal Modeling (2nd edition;
  edited by Koch, C. and Segev, I.), MIT press, Cambridge, 1996.

  This simplified model was introduced in:

  Destexhe, A., Bal, T., McCormick, D.A. and Sejnowski, T.J.
  Ionic mechanisms underlying synchronized oscillations and propagating
  waves in a model of ferret thalamic slices. Journal of Neurophysiology
  76: 2049-2070, 1996.

  See also http://www.cnl.salk.edu/~alain



  Alain Destexhe, Salk Institute and Laval University, 1995

  Threadsafe version adabted by Scott McElroy, SUNY Dowsntate, 2025
-----------------------------------------------------------------------------
ENDCOMMENT


NEURON {
    THREADSAFE
    POINT_PROCESS GABAB_SM
    RANGE R, G, g
    NONSPECIFIC_CURRENT i
    RANGE Cmax, Cdur
    RANGE K1, K2, K3, K4, KD, Erev, warn, cutoff
}
UNITS {
    (nA) = (nanoamp)
    (mV) = (millivolt)
    (umho) = (micromho)
    (mM) = (milli/liter)
}

PARAMETER {
    Cmax = 0.5 (mM)
    Cdur = 0.3 (ms)
    K1 = 0.52 (/ms mM)
    K2 = 0.0013 (/ms)
    K3 = 0.098 (/ms)
    K4 = 0.033 (/ms)
    KD = 100
    n = 4
    Erev = -95 (mV)
    warn = 0
    cutoff = 1e12
}

ASSIGNED {
    v (mV)
    i (nA)
    g (umho)
    Gn
    R
    edc
    Rinf
    Rtau (ms)
    Beta (/ms)
}

STATE {
    Ron Roff
    G
    T
}

INITIAL {
    R = 0
    G = 0
    Ron = 0
    Roff = 0
    T = 0
    Rinf = K1*Cmax/(K1*Cmax + K2)
    Rtau = 1/(K1*Cmax + K2)
    Beta = K2
}

BREAKPOINT {
    SOLVE bindkin METHOD derivimplicit
    if (G < cutoff) {
        Gn = G*G*G*G
        g = Gn / (Gn+KD)
    } else {
        if (!warn) {
            printf("gabab.mod WARN: G = %g too large\n", G)
            warn = 1
        }
        g = 1
    }
    i = g*(v - Erev)
}

DERIVATIVE bindkin {
    T' = -T/Cdur
    Ron' = K1 * T * (1 - Ron - Roff) - K2 * Ron
    Roff' = -K2 * Roff
    R = Ron + Roff
    G' = K3 * R - K4 * G
}

NET_RECEIVE(weight) {
    T = T + weight * Cmax
}