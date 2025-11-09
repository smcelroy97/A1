NEURON {
  POINT_PROCESS NoiseIClampControlled2
  NONSPECIFIC_CURRENT i
  RANGE mu0, sigma0, mu_gain, sigma_gain, noise, ctrl
  POINTER pctrl
}

UNITS {
  (nA) = (nanoamp)
}

PARAMETER {
  mu0 = 0 (nA) : constant part of mu
  sigma0 = 0 (nA) : constant part of sigma
  mu_gain = 0 (nA) : effect of pctrl on mu
  sigma_gain = 0 (nA) : effect of pctrl on sigma
  noise = 0  : zero-mean noise played from Python (dimensionless)
}

ASSIGNED {
  v (mV)
  i (nA)
  pctrl : pointer to a control signal
  ctrl
}

INITIAL {
  ctrl = 0.0         : avoid NaNs before pointer is set
}

LOCAL mu, sigma

BREAKPOINT {
  ctrl = pctrl * 10
  mu = mu0 + mu_gain * pctrl
  sigma = sigma0 + sigma_gain * pctrl
  if (sigma < 0) {
      sigma = 0
  }
  i = -(mu + sigma * noise)
}
