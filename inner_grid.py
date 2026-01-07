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

def eval_script(job):
    cfg={key: space[index] for key, space, index in zip(params, spaces, job.indexes)}
    cfg.update(outer_cfg)
    cfg['label'] = f"{outer_label}_{job.label}"

    cfg['job_num'] = f"{job.label}"
    return cfg

with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(generate_config, all_jobs)

results_df = pandas.DataFrame(list(results)).set_index('job_num').drop(columns=['_runner', '_batchtk_label_pointer', '_batchtk_dir_pointer'])
print(results_df)

results_df.to_csv(f"grid_{outer_label}.csv")

message = {
    'label': results_df['label'].iloc[2],
    'ou_ramp_offset': results_df['ou_ramp_offset'].iloc[2],
    'description': str(results_df['ou_ramp_offset'].describe()),
}

with get_comm() as comm: # communicate results back to outer optuna script --
    comm.send(message)


#TODO, define any cfg parameters as necessary here, corresponding modification to scriptMUT.py, scriptWT.py
# KEEP batchnum for labeling purposes, each grid will create 2 sets of outputs with different batchnum
# otherwise files will be clobbered


def eval_script(script, cfg):
    inner_cfg = {key: val for key, val in cfg.items() if key in parameter_list}
    inner_cfg.update({'saveFolder': '.', 'simLabel': LABEL_POINTER})
    return trial(
        config=inner_cfg,
        label='inner',
        tid="{}_{}".format(cfg['batchnum'], script),
        dispatcher_constructor=LocalDispatcher,
        project_path='.',
        output_path='./inner_out',
        submit_constructor=SHSubmitSFS,
        dispatcher_kwargs=None,
        submit_kwargs={'command': 'python {}.py'.format(script)},
        interval=1,
        check_storage=False, # don't check data storage for now 2/2 ongoing code refactor:
        cleanup=False, # for debugging purposes, keep all the files, manually cleanup before running script
    )


results = {}

#eval_script('script0', outer_cfg)  # Run first script sequentially
# run trials
for script in scripts:
    result = eval_script(script, outer_cfg)
    results[script] = result['fx']

print("Results:", results) # do whatever logic here

with get_comm() as comm: # communicate results back to outer optuna script --
    print(id(comm))
    comm.send({'WT': results['scriptWT'], 'MUT': results['scriptMUT']})
