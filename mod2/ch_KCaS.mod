TITLE calcium-activated potassium channel (non-voltage-dependent)

COMMENT
Ca2+ activated K+ channel (not voltage dependent)

From:  original said for granule cells, but used in all the cell types

Updates:
2014 December (Marianne Bezaire): documented
ENDCOMMENT

NEURON {
    SUFFIX ch_KCaS
    USEION ca READ cai
    USEION k WRITE ik
    RANGE gbar, ik, g, m
}

UNITS {
    (mA) = (milliamp)
    (mV) = (millivolt)
    (molar) = (1/liter)
    (mM) = (millimolar)
}

PARAMETER {
    gbar = 0.001 (mho/cm2)
    v (mV)
    cai = 5e-5 (mM)
    ek = -80 (mV)
    celsius = 36 (degC)
}

STATE {
    m
}

ASSIGNED {
    ik (mA/cm2)
    g (mho/cm2)
    minf
    mtau (ms)
    tadj
}

INITIAL {
    tadj = 3 ^ ((celsius - 22.0)/10)
    rates(v, cai)
    m = minf
}

BREAKPOINT {
    SOLVE states METHOD cnexp
    g = gbar * m
    ik = g * (v - ek)
}

DERIVATIVE states {
    rates(v, cai)
    m' = (minf - m) / mtau
}

PROCEDURE rates(v (mV), cai (mM)) {
    minf = cai / (cai + 0.0001)
    mtau = 2.0
}