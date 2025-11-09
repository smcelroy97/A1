NEURON {
  POINT_PROCESS NoiseIClampControlled
  NONSPECIFIC_CURRENT i
  RANGE mu, sigma, noise, ctrl
  POINTER pmu, psigma
}

UNITS {
  (nA) = (nanoamp)
}

PARAMETER {
  mu = 0 (nA)
  sigma = 0 (nA)
  noise = 0  : zero-mean noise played from Python (dimensionless)
}

ASSIGNED {
  i (nA)
  pmu    : mean current pointer (nA)
  psigma : current std. pointer (nA)
  ctrl
}

INITIAL {
  ctrl = 0.0
}

LOCAL s

BREAKPOINT {
  :i = -(pmu + sigma * noise)
  ctrl = psigma * 10
  s = sigma + psigma
  if (s < 0) {
      s = 0
  }
  i = -mu + s * noise
}
