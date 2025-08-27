TITLE Fast delayed rectifier potassium channel (voltage dependent, for neurogliaform family)

COMMENT
Fast delayed rectifier potassium channel (voltage dependent, for neurogliaform family)

Ions: k

Style: quasi-ohmic

From: Yuen and Durand, 1991 (squid axon)

Updates:
2014 December (Marianne Bezaire): documented
? ? (Aradi): shifted the voltage dependence by 16 mV
ENDCOMMENT

NEURON {
    SUFFIX Kdrfastngf
    USEION k WRITE ik
    RANGE gbar, ik, g, m, h
}

UNITS {
    (mA) = (milliamp)
    (mV) = (millivolt)
}

PARAMETER {
    gbar = 0.01 (mho/cm2)
    v (mV)
    ek = -80 (mV)
    celsius = 36 (degC)
}

STATE {
    m
    h
}

ASSIGNED {
    ik (mA/cm2)
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
    ik = g * (v - ek)
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