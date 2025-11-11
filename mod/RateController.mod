NEURON {
  POINT_PROCESS RateController
  RANGE tau, r0, k, kp, rate, u, z, z0, t0
}

PARAMETER {
  tau = 50 (ms)         : EMA time constant for rate
  r0  = 5.0             : target rate (Hz)
  k   = 0.02            : adaptation gain (integral)
  kp  = 0.02            : adaptation gain (proportional)
  z0 = 0.0              : initial value of z
  t0  = 0 (ms)
}

STATE {
  rate                  : (Hz)
  u                     : control variable (internal)
}

ASSIGNED {
  z (Hz)          : control output
}

INITIAL {
  rate = 0.0
  u = z0
  z = z0
}

BREAKPOINT {
  SOLVE states METHOD cnexp
  if (t >= t0) {
    z = kp * (r0 - rate) + u
  } else {
    z = z0
  }
}

DERIVATIVE states {
  if (t < t0) {
    rate' = 0
    u'    = 0
  } else {
    rate' = -rate/tau
    u'    = k * (r0 - rate)
  }
}

NET_RECEIVE (w) {
  if (t >= t0) {
    : Each spike bumps the EMA by 1000/tau (so steady-state == spike freq in Hz)
    rate = rate + w * (1000.0/tau)
  }
}
