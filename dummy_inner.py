# this code:
# pass through channel parameters from outer_search
# generates a grid search through cfg.ou_* (ou_ramp_offset)
from batchtk.runtk import LocalDispatcher, SHSubmitSFS, SHSubmit
from batchtk.runtk.trial import trial, LABEL_POINTER
from batchtk.utils.storage import SQLiteStorage
#TODO debug concurrent.futures threading lock issues...
from batchtk.runtk import RunConfig, get_comm
from batchtk import runtk
import os, itertools
from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple
import pandas

outer_cfg = RunConfig()

outer_cfg['label'] = 0
outer_cfg['multiply_parameters'] = {
    'kdr0': {'factor': 1},
    'cal0': {'factor': 1},
}

outer_cfg.update()

outer_label = outer_cfg.pop('label')

def dot_serialize(struct, current=''):
    """
    Recursively traverses dictionary, generate dot-separated paths to all non-dict values
    """
    paths = []
    for key, value in struct.items():
        next = f"{current}.{key}" if current else key
        if isinstance(struct[key], dict):
            paths.extend(dot_serialize(value, next))
        else:
            paths.append( (next, value))
    return paths

outer_cfg.update()
outer_cfg = dict(dot_serialize(outer_cfg))

param_space = {
    'ou_ramp_offset': [0.75, 1.0, 2.00, 3.00, 4.00],
}

params, spaces = zip(*param_space.items())
space_indexes = [range(len(space)) for space in spaces]
#all_indexes = itertools.product(*space_indexes) # can generate ids the space index, enumerate index or hash index
Job = namedtuple('Job', ['label', 'indexes'])
all_jobs = (Job(label, indexes) for label, indexes in enumerate(itertools.product(*space_indexes)))

def generate_config(job):
    cfg={key: space[index] for key, space, index in zip(params, spaces, job.indexes)}
    cfg.update(outer_cfg)
    cfg['label'] = f"{outer_label}_{job.label}"
    return cfg

with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(generate_config, all_jobs)

results_list = []
for result in results:
    results_list.append(pandas.Series(results))

results_df = pandas.DataFrame(results_list)

print(results_df)

#with get_comm() as comm: # communicate results back to outer optuna script --
#    comm.send({'WT': results['scriptWT'], 'MUT': results['scriptMUT']})
