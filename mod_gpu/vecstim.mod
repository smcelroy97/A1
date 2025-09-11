: $Id: vecstim.mod,v 1.3 2010/12/13 21:29:27 samn Exp $ 
:  Vector stream of events

NEURON {
  THREADSAFE
       ARTIFICIAL_CELL VecStim 
}

ASSIGNED {
	index
	etime (ms)
	space
}

INITIAL {
	index = 0
	if (index > 0) {
		if (etime - t>=0) {
			net_send(etime - t, 1)
		} else {
			printf("Event in the stimulus vector at time %g is omitted since has value less than t=%g!\n", etime, t)
			net_send(0, 2)
		}
	}
}

NET_RECEIVE (w) {
	if (flag == 1) { net_event(t) }
	if (flag == 1 || flag == 2) {
		if (index > 0) {	
			if (etime - t>=0) {
				net_send(etime - t, 1)
			} else {
				printf("Event in the stimulus vector at time %g is omitted since has value less than t=%g!\n", etime, t)
				net_send(0, 2)
			}
		}
	}
}

