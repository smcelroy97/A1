from batchtk.runtk import LocalDispatcher, SHSubmitSFS
from batchtk.utils.storage import SQLiteStorage
from batchtk.runtk.trial import trial
import os, itertools
from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple
import pandas
# more flexible import of header.py

path = os.getcwd()

param_space = {
    'multiply_parameters.kdr0.factor': [1.0, 2.0, 3.0],
    'multiply_parameters.cal0.factor': [0.5, 1.0, 1.5],
}


storage_kwargs = dict(label='trials', directory='./batch',
                      filename='outer_search.sqlite.db', timeout=30)

params, spaces = zip(*param_space.items())
space_indexes = [range(len(space)) for space in spaces]
#all_indexes = itertools.product(*space_indexes) # can generate ids the space index, enumerate index or hash index
Job = namedtuple('Job', ['label', 'indexes'])
all_jobs = (Job(label, indexes) for label, indexes in enumerate(itertools.product(*space_indexes)))

def generate_config(job):
    cfg={key: space[index] for key, space, index in zip(params, spaces, job.indexes)}
    cfg['label'] = job.label
    return cfg

def eval_inner(job):
    cfg = {param: index for param, index in zip(params, job.indexes)}
    cfg['batch_num'] = job.label  # pass outer trial number to inner script for labeling...
    tid = "outer_{}".format(job.label)
    data = trial(
        config=cfg,
        label='batch',
        tid=tid,
        dispatcher_constructor=LocalDispatcher,
        project_dir=path,
        output_dir='./batch',
        submit_constructor=SHSubmitSFS, #ZSHSubmitSFS ?, # running on the hpc where the zsh requires some mpi finagling.
        dispatcher_kwargs=None,
        submit_kwargs={'command': 'python inner_grid.py'}, # nested, external optimizer considers both parameters, internal performs 2 operations.
        interval=1,
        storage_kwargs=storage_kwargs,
        report=('path', 'data'),
    )
    return data


with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(generate_config, all_jobs)

results_df = pandas.DataFrame(list(results))
print(results_df)

results_df.to_csv(f"batch/complete_batch.csv")
