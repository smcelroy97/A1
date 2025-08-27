TITLE L-type calcium channel (voltage dependent)

COMMENT
L-Type Ca2+ channel (voltage dependent)

Ions: ca

Style: ghk

From: Jaffe et al, 1994


Updates:
2014 December (Marianne Bezaire): documented
ENDCOMMENT

NEURON {
    SUFFIX CavL
    USEION ca READ cai, eca WRITE ica
    RANGE gbar, ica, g, m, h
}

UNITS {
    (mA) = (milliamp)
    (mV) = (millivolt)
    (mM) = (millimolar)
}

PARAMETER {
    gbar = 0.001 (mho/cm2)
    v (mV)
    cai = 5e-5 (mM)
    eca = 140 (mV)
    celsius = 36 (degC)
}

STATE {
    m
    h
}

ASSIGNED {
    ica (mA/cm2)
    g (mho/cm2)
    minf
    hinf
    mtau (ms)
    htau (ms)
    tadj
}

INITIAL {
    tadj = 3 ^ ((celsius - 22.0)/10)
    rates(v)
    m = minf
    h = hinf
}

BREAKPOINT {
    SOLVE states METHOD cnexp
    g = gbar * m * h
    ica = g * (v - eca)
}

DERIVATIVE states {
    rates(v)
    m' = (minf - m) / mtau
    h' = (hinf - h) / htau
}

PROCEDURE rates(v (mV)) {
    minf = 1 / (1 + exp(-(v+20)/6.5))
    mtau = 1.0
    hinf = 1 / (1 + exp((v+25)/2.5))
    htau = 30.0
}