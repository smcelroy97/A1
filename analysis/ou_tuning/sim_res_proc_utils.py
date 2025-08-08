from pathlib import Path
import sys

dirpath_repo_root = Path(__file__).resolve().parents[3]
dirpath_self = Path(__file__).resolve().parent
sys.path.append(str(dirpath_repo_root))
#sys.path.append(str(dirpath_self))

from scipy.ndimage import median_filter

from analysis.ou_tuning import netpyne_res_parse_utils as utils
from analysis.ou_tuning import data_proc_utils as proc


def calc_rates_and_cvs(
        sim,   # NetPyNE sim object obtained after a simulation
        t_limits: tuple[float, float] | None = None,   # time window used for calculation
        nspikes_min: int = 3   # min. number of spikes to use a cell in CV calculation
        ) -> dict:
    
    if t_limits is None:
        t_limits = (0, sim.cfg.duration / 1000)
    # Convert NetPyNE object to a dict (same as stored in pkl files)
    sim_result = utils.prepare_sim_result(sim)
    # Extract spikes
    all_spikes = utils.get_net_spikes(sim_result)   # cells combined
    cell_spikes = utils.get_net_spikes(sim_result,
                                       combine_cells=False)   # per cell
    # Get the size of each pop.
    ncells = utils.get_net_size(sim_result)   # {pop: ncells}
    # Calculate rates and CVs
    rates = proc.calc_net_rates(all_spikes, time_limits=t_limits,
                                ncells=ncells)
    cvs = proc.calc_net_cvs(cell_spikes, time_limits=t_limits,
                            nspikes_min=nspikes_min, avg_result=True)
    # Combine the result
    res = {'rates': rates, 'cvs': cvs, 't_limits_r': t_limits,
           'nspikes_min': nspikes_min}
    return res

def calc_v_stats(
        sim,   # NetPyNE sim object obtained after a simulation
        t_limits: tuple[float, float] | None = None,   # time window used for calculation
        med_win: float = 0.1   # time window of the median filter
        ) -> dict:
    if t_limits is None:
        t_limits = (0, sim.cfg.duration / 1000)
    # Convert NetPyNE object to a dict (same as stored in pkl files)
    sim_result = utils.prepare_sim_result(sim)
    # Extract voltage traces
    V = utils.get_voltages_xr(sim_result, t_limits, ms=False)
    # Calculate voltage stats
    res = {'v_med_min': {}, 'v_med_max': {},
           't_limits_v': t_limits, 'med_win': med_win}
    dt = utils.get_timestep(sim_result)
    for pop, Vmat in V.items():
        if Vmat is None:
            continue
        Vmed = median_filter(Vmat.values, size=(1, int(med_win / dt)))
        res['v_med_min'][pop] = Vmed.ravel().min()
        res['v_med_max'][pop] = Vmed.ravel().max()
    return res
