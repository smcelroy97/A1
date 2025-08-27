: $Id: nsloc.mod,v 1.7 2013/06/20  salvad $
: from nrn/src/nrnoc/netstim.mod
: modified to use allow for time-dependent intervals

NEURON {
    ARTIFICIAL_CELL DynamicNetStim
    RANGE interval, number, start, id, type, subtype, fflag, mlenmin, mlenmax, check_interval, noise
    THREADSAFE
}

PARAMETER {
    interval = 100 (ms) <1e-9,1e9>
    number = 3000 <0,1e9>
    start = 1 (ms)
    noise = 0 <0,1>
    id = -1
    type = -1
    subtype = -1
    fflag = 1
    check_interval = 1.0 (ms)
}

ASSIGNED {
    event (ms)
    last_interval (ms)
    transition
    on
    ispike
}

FUNCTION invl(mean (ms)) (ms) {
    if (mean <= 0.) {
        mean = .01 (ms)
    }
    if (noise == 0) {
        invl = mean
    } else {
        invl = (1. - noise)*mean + noise*mean*erand()
    }
}

FUNCTION erand() {
    erand = -log(1.0 - nrn_random_pick())
}

INITIAL {
    on = 0
    ispike = 0
    if (noise < 0) {
        noise = 0
    }
    if (noise > 1) {
        noise = 1
    }
    if (start >= 0 && number > 0) {
        on = 1
        event = start + invl(interval) - interval*(1. - noise)
        if (event < 0) {
            event = 0
        }
        net_send(event, 3)
    }
}

PROCEDURE init_sequence(t (ms)) {
    if (number > 0) {
        on = 1
        event = 0
        ispike = 0
    }
}

PROCEDURE next_invl() {
    if (number > 0) {
        event = invl(interval)
    }
    if (ispike >= number) {
        on = 0
    }
}

NET_RECEIVE (w) {
    if (flag == 0) {
        if (w > 0 && on == 0) {
            init_sequence(t)
            next_invl()
            event = event - interval*(1. - noise)
            net_send(event, 1)
        } else if (w < 0) {
            on = 0
        }
    }
    if (flag == 3) {
        if (on == 1) {
            init_sequence(t)
            net_send(0, 1)
            net_send(2*check_interval, 4)
        }
    }
    if (flag == 1 && on == 1) {
        ispike = ispike + 1
        net_event(t)
        next_invl()
        transition = 0
        if (on == 1) {
            net_send(event, 1)
        }
    }
    if (flag == 5 && on == 1 && transition == 1) {
        ispike = ispike + 1
        net_event(t)
        next_invl()
        if (on == 1) {
            net_send(event, 5)
        }
    }
    if (flag == 4 && on == 1) {
        if (interval < last_interval) {
            next_invl()
            transition = 1
            net_send(event, 5)
        }
        last_interval = interval
        net_send(check_interval, 4)
    }
    if (flag == 1 && on == 0) {
        net_event(t)
    }
}

COMMENT
Presynaptic spike generator
---------------------------
This mechanism generates periodic or noisy (Poisson-distributed) spike trains.
ENDCOMMENT
