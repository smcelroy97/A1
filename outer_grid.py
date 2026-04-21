from batchtk.runtk import LocalDispatcher, SHSubmitSFS
from batchtk.utils.storage import SQLiteStorage
from batchtk.runtk.trial import trial
import os
import itertools
from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple
import pandas
from batchtk.utils.parser import TomlParser
import numpy as np
import hashlib
import json
# more flexible import of header.py


path = os.getcwd()

param_space = {
    'multiply_parameters.kdr0.factor': [3],
    'multiply_parameters.pas0.factor': [1, 2, 3]
}

parser = TomlParser(file_path='outer_slurm.toml')
Submit = parser.get_submit_class()

def batch_name_from_param_space(param_space):
    parts = []
    for key, values in param_space.items():
        short_name = key.split(".")[1]
        values_slug = "-".join(str(v).replace(".", "p") for v in values)
        parts.append(f"{short_name}_{values_slug}")
    return "__".join(parts)

def make_job_label(params, spaces, indexes):
    parts = []
    for param, space, idx in zip(params, spaces, indexes):
        short_name = param.split(".")[1]
        value_slug = str(space[idx]).replace(".", "p")
        parts.append(f"{short_name}={value_slug}")
    return "__".join(parts)

params, spaces = zip(*param_space.items())
space_indexes = [range(len(space)) for space in spaces]

batch_slug = batch_name_from_param_space(param_space)
batch_dir = os.path.join("./batch", batch_slug)
os.makedirs(batch_dir, exist_ok=True)

storage_kwargs = dict(
    label='trials',
    directory=batch_dir,
    filename='grid.sqlite.db',
    timeout=30
)

batch_slug = batch_name_from_param_space(param_space)
batch_dir = os.path.join("./batch", batch_slug)
os.makedirs(batch_dir, exist_ok=True)

Job = namedtuple('Job', ['label', 'indexes'])
all_jobs = (
    Job(label=make_job_label(params, spaces, indexes), indexes=indexes)
    for indexes in itertools.product(*space_indexes)
)

def generate_config(job):
    cfg = {key: space[index] for key, space, index in zip(params, spaces, job.indexes)}
    cfg['label'] = job.label
    return cfg


def eval_inner(job):
    cfg = {param: index for param, index in zip(params, job.indexes)}
    cfg['batch_id'] = job.label  # pass outer trial number to inner script for labeling...
    tid = "grid{}".format(job.label)
    data = trial(
        config=cfg,
        label='batch',
        tid=tid,
        dispatcher_constructor=LocalDispatcher,
        project_dir=path,
        output_dir='./batch',
        submit_constructor=Submit,  # ZSHSubmitSFS ?, # running on the hpc where the zsh requires some mpi finagling.
        dispatcher_kwargs=None,
        submit_kwargs={'command': 'python inner_grid.py'},  # nested, external optimizer considers both parameters, internal performs 2 operations.
        interval=1,
        storage_kwargs=storage_kwargs,
        report=('path', 'data'),
    )
    return data


with ThreadPoolExecutor(max_workers=1) as executor:
    results = executor.map(eval_inner, all_jobs)

results_df = pandas.DataFrame(list(results))
print(results_df)

results_df.to_csv(f"batch/complete_batch.csv")
