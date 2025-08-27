: Python callback from BEFORE STEP

NEURON {
  POINT_PROCESS beforestep_callback
  POINTER ptr
}

ASSIGNED {
  ptr
}

INITIAL {
  : No initialization needed
}

BEFORE STEP {
  : Callback not supported in CoreNEURON/threads
}

PROCEDURE set_callback() {
  : Callback assignment not supported in CoreNEURON/threads
}