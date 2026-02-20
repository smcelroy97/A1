# this code:
# pass through channel parameters from outer_search
# generates a grid search through cfg.ou_* (ou_ramp_offset)
from batchtk.runtk import LocalDispatcher, SHSubmitSFS, SHSubmit
from batchtk.runtk.trial import trial, LABEL_POINTER, DIR_POINTER
from batchtk.utils.parser import TomlParser
from batchtk.utils.storage import SQLiteStorage
#  TODO debug concurrent.futures threading lock issues...
from batchtk.runtk import RunConfig, get_comm
from batchtk import runtk
import os, itertools
from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple
import pandas, json


parser = TomlParser(file_path='inner_shell.toml')
Submit = parser.get_submit_class()

path = os.getcwd()
outer_cfg = RunConfig()

outer_cfg['batch_id'] = 0
outer_cfg['multiply_parameters'] = {
    'kdr0': {'factor': 1}
}

outer_cfg.update()

outer_label = f"grid{outer_cfg['batch_id']}"


def dot_serialize(struct, current=''):
    """
    Recursively traverses dictionary, generate dot-separated paths to all non-dict values
    """
    paths = []
    for key, value in struct.items():
        if key[0] == '_':  # skip all internal handlers to cfg for dot serialization
            continue
        _next = f"{current}.{key}" if current else key
        if isinstance(struct[key], dict):
            paths.extend(dot_serialize(value, _next))
        else:
            paths.append((_next, value))
    return paths


outer_cfg = dict(dot_serialize(outer_cfg))

param_space = { # expand these parameter spaces...
    'ou_ramp_offset': [1.0, 4.00],
    'bkg_r': [25, 125],
#    'bkg_w': [0.1, 1.0],
    }

# NetStim inputs (weak, just to randomly jitter the cells between steady-states)

os.makedirs(f"./batch/{outer_label}", exist_ok=True)

params, spaces = zip(*param_space.items())
space_indexes = [range(len(space)) for space in spaces]
# all_indexes = itertools.product(*space_indexes) # can generate ids the space index, enumerate index or hash index
Job = namedtuple('Job', ['label', 'indexes'])
all_jobs = (Job(label, indexes) for label, indexes in enumerate(itertools.product(*space_indexes)))


def eval_script(job):
    cfg= {key: space[index] for key, space, index in zip(params, spaces, job.indexes)}
    cfg.update(outer_cfg)
    cfg.update({'saveFolder': DIR_POINTER, 'simLabel': LABEL_POINTER})
    tid = f"{outer_label}_{job.label}"
    # # save a copy of the config used for this job so we can reproduce or inspect it later
    # configs_dir = os.path.join(path, 'batch', outer_label)
    # try:
    #     os.makedirs(configs_dir, exist_ok=True)
    #     cfg_file = os.path.join(configs_dir, f"batch_{tid}_cfg.json")
    #     with open(cfg_file, 'w') as cf:
    #         json.dump(cfg, cf, default=str, indent=2)
    # except Exception as e:
    #     print(f"Warning: failed to save config for {tid}: {e}")
    data = trial(
        config=cfg,
        label='batch',
        tid=tid,
        dispatcher_constructor=LocalDispatcher,
        project_dir=path,
        output_dir=f"./batch/{outer_label}",
        submit_constructor=Submit, #ZSHSubmitSFS ?, # running on the hpc where the zsh requires some mpi finagling.
        dispatcher_kwargs=None,
        submit_kwargs={'command': 'mpirun nrniv -python -mpi init.py'},
        interval=1,
        storage_constructor=None,
        #storage_kwargs=storage_kwargs, # for now no checkpointing
        report=('path', 'data'),
    )
    return data

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(eval_script, all_jobs)


results_df = pandas.DataFrame(list(results))
print(results_df)

csv_file = f"./batch/{outer_label}/results.csv"
results_df.to_csv(csv_file)

def inner_analysis():# don't need to pass
    """
    #TODO nikita populate this function with whatever data needs to be stored ...
    sim_analysis takes sim object and calculates any notable values that can be gained from sim object
    #NOTES
    single numeric values and strings can be sent via message and collated in an sql/pandas structure for organization
    or, can save any larger values to desired format, and open them using path (unique to each job)
    """
    data_table = {}
    # larger data structures can be stored in a separate file...

    # note, no guarantee that the results_df is sorted properly...
    for trial in results_df.itertuples():
        data_table[trial.trial_label] = trial.csv
    # do whatever data calculations on the results_df, from loaded trial.csv values, or pass through,
    # however, for searches we want a single, or multiple, fitness scores.

    json_file = f"./batch/{outer_label}/csv.json"

    message = json.dumps({
        'min': results_df['hbm3'].min(),
        'max': results_df['hbm3'].max(),
        'mean': results_df['hbm3'].mean(),
        'json': json_file,
        'csv': csv_file})
    with open(json_file, "w") as fptr:
        json.dump(data_table, fptr)

    print(message)

    return message

message = inner_analysis()

# TODO by next meeting
# 1. TODO organize nested grid search I/O structures---
# 1. TODO return should be some data structure? (xarray)
# 1. TODO load all trials here--

# TODO long term goals
# 2. TODO add some comparative metrics --
# 2. TODO metrics for stability, check w/ Nikita

with get_comm() as comm: # communicate results back to outer script --
    comm.send(message)


print(message)