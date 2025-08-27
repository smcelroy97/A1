NEURON {
    SUFFIX icanINT
    USEION other2 WRITE iother2 VALENCE 1
    USEION Ca READ Cai VALENCE 2
    USEION ca READ cai
    RANGE gbar, i, g, ratc, ratC
    GLOBAL m_inf, tau_m, beta, cac, taumin, erev, x
}

UNITS {
    (mA) = (milliamp)
    (mV) = (millivolt)
    (molar) = (1/liter)
    (mM) = (millimolar)
}

PARAMETER {
    v       (mV)
    celsius = 36    (degC)
    erev = 10       (mV)
    cai    = .00005 (mM)
    Cai    = .00005 (mM)
    gbar   = 1e-5   (mho/cm2)
    beta   = 2.5    (1/ms)
    cac    = 1e-4   (mM)
    taumin = 0.1    (ms)
    ratc   = 1
    ratC   = 1
    x      = 2
}

STATE {
    m
}

ASSIGNED {
    i        (mA/cm2)
    iother2  (mA/cm2)
    g        (mho/cm2)
    m_inf
    tau_m    (ms)
    tadj
}

INITIAL {
    tadj = 3.0 ^ ((celsius - 22.0) / 10)
    evaluate_fct(v, cai, Cai)
    m = m_inf
}

BREAKPOINT {
    SOLVE states METHOD cnexp
    g = gbar * m * m
    i = g * (v - erev)
    iother2 = i
}

DERIVATIVE states {
    evaluate_fct(v, cai, Cai)
    m' = (m_inf - m) / tau_m
}

UNITSOFF

PROCEDURE evaluate_fct(v (mV), cai (mM), Cai (mM)) {
    LOCAL alpha2, tcar
    tcar = ratc * cai + ratC * Cai
    alpha2 = beta * (tcar / cac) ^ x
    tau_m = 1 / (alpha2 + beta) / tadj
    m_inf = alpha2 / (alpha2 + beta)
    if (tau_m < taumin) {
        tau_m = taumin
    }
}
UNITSON






