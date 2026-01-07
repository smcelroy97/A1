from batchtk.runtk import LocalDispatcher, SHSubmitSFS
from batchtk.utils.storage import SQLiteStorage
from batchtk.runtk.trial import trial as runtk_trial
import os, itertools
from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple
# more flexible import of header.py

path = os.getcwd()

param_space = {
    'multiply_parameters.kdr0.factor': [1.0, 2.0, 3.0],
    'multiply_parameters.cal0.factor': [0.5, 1.0, 1.5],
}


log = SQLiteStorage(label='trials', directory='./outer_out',
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

"""
def eval_inner(job):
    cfg = {param: index for param, index in zip(params, job.indexes)}
    cfg['batchnum'] = job.label  # pass outer trial number to inner script for labeling...
    tid = "outer_{}".format(job.label)
    data = runtk_trial(
        config=cfg,
        label='outer',
        tid=tid,
        dispatcher_constructor=LocalDispatcher,
        project_path=path,
        output_path='./outer_out',
        submit_constructor=SHSubmitSFS, #ZSHSubmitSFS ?, # running on the hpc where the zsh requires some mpi finagling.
        dispatcher_kwargs=None,
        submit_kwargs={'command': 'python inner_grid.py'}, # nested, external optimizer considers both parameters, internal performs 2 operations.
        interval=1,
        report=('path', 'data')
    )
    #loss = [float(data[key]) for key in metrics]
    #return loss
    pass
"""
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(generate_config, all_jobs)

for result in results:
    print(result)




#sampler = samplers[ALGO](seed=0)

#study   = optuna.create_study(directions=directions,
#                              storage="sqlite:///{}/outer_out_search.db".format(path, ALGO),
#                              load_if_exists=True,
#                              sampler=sampler,
#                              study_name='search'.format(ALGO))

#study.optimize(eval_inner, n_trials=6, timeout=300)
