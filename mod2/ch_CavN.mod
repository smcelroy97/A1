TITLE N-type calcium channel (voltage dependent)

COMMENT
N-Type Ca2+ channel (voltage dependent)

Ions: ca

Style: quasi-ohmic

From: Aradi and Holmes, 1999

Updates:
2014 December (Marianne Bezaire): documented
ENDCOMMENT

NEURON {
    SUFFIX CavN
    USEION ca READ cai, eca WRITE ica
    RANGE gbar, ica, g, m, h
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
    minf = 1 / (1 + exp(-(v+30)/6.5))
    mtau = 1.0
    hinf = 1 / (1 + exp((v+35)/2.5))
    htau = 30.0
}