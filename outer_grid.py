from batchtk.runtk import LocalDispatcher, SHSubmitSFS
from batchtk.utils.storage import SQLiteStorage
from batchtk.runtk.trial import trial
import os, itertools
from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple
import pandas
from batchtk.utils.parser import TomlParser
# more flexible import of header.py

path = os.getcwd()

param_space = {
    'multiply_parameters.kdr0.factor': [1.0, 3.0]
}

parser = TomlParser(file_path='outer_slurm.toml')
Submit = parser.get_submit_class()

storage_kwargs = dict(label='trials', directory='./batch',
                      filename='grid.sqlite.db', timeout=30)

os.makedirs('./batch', exist_ok=True)
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
