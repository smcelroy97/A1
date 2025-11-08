NEURON {
  POINT_PROCESS NoiseIClampControlled
  NONSPECIFIC_CURRENT i
  RANGE mu, sigma, noise
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
}

BREAKPOINT {
  i = -(pmu + sigma * noise)
}
