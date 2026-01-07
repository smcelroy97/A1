# this code:
# pass through channel parameters from outer_search
# generates a grid search through cfg.ou_* (ou_ramp_offset)
from batchtk.runtk import LocalDispatcher, SHSubmitSFS, SHSubmit
from batchtk.runtk.trial import trial, LABEL_POINTER, DIR_POINTER
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
outer_cfg['batch_num'] = 0
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


os.makedirs(f"./outer_out/{outer_label}", exist_ok=True)
storage_kwargs = dict(label='trials', directory=f"./outer_out/{outer_label}",
                      filename='inner_grid.sqlite.db', timeout=30)

params, spaces = zip(*param_space.items())
space_indexes = [range(len(space)) for space in spaces]
#all_indexes = itertools.product(*space_indexes) # can generate ids the space index, enumerate index or hash index
Job = namedtuple('Job', ['label', 'indexes'])
all_jobs = (Job(label, indexes) for label, indexes in enumerate(itertools.product(*space_indexes)))


def eval_script(job):
    cfg={key: space[index] for key, space, index in zip(params, spaces, job.indexes)}
    cfg.update(outer_cfg)
    cfg.update({'saveFolder': DIR_POINTER, 'simLabel': LABEL_POINTER})
    tid = f"{outer_label}_{job.label}"
    data = trial(
        config=cfg,
        label='batch',
        tid=tid,
        dispatcher_constructor=LocalDispatcher,
        project_dir=path,
        output_dir='./outer_out',
        submit_constructor=SHSubmitSFS, #ZSHSubmitSFS ?, # running on the hpc where the zsh requires some mpi finagling.
        dispatcher_kwargs=None,
        submit_kwargs={'command': 'mpiexec -np 4 nrniv -python -mpi init.py'},
        interval=1,
        storage_kwargs=storage_kwargs,
        report=('path', 'data'),
    )
    loss = [float(data[key]) for key in ['offset', 'hbm', 'path']]
    return loss

with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(eval_script, all_jobs)

results_df = pandas.DataFrame(list(results)).set_index('job_num').drop(columns=['_runner', '_batchtk_label_pointer', '_batchtk_dir_pointer'])
print(results_df)

results_df.to_csv(f"grid_{outer_label}.csv")

message = {
    'label': results_df['label'].iloc[2],
    'ou_ramp_offset': results_df['offset'].iloc[2],
    'spike_data': str(results_df['hbm'].describe()),
    'path': results_df['path'].iloc[2],
}

with get_comm() as comm: # communicate results back to outer script --
    comm.send(message)


print(message)