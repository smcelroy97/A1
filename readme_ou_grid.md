# New instruction

## GIT

The branch `ou-gridSM` on Github is up-to-date.

The simplest way to get it locally, is to clone the repo anew.

Another way is:
- Backup your recent changes in the tracked files
- `git checkout ou-gridSM`
- `git add .`
- `git stash` (clean all uncommitted changes)
- `git reset --hard 968fb0f` (it will REMOVE all recent changes in the tracked files from the disk)
- `git stash`
- `git pull`

We will discuss the details of shared work later. Until then, you can just work in `ou-gridSM`, I won't touch it.
I will merge my branch to `ou-grid` from time to time, and it may contain useful updates. So I recommend you before pushing your branch to Github do the following:
- `git checkout ou-gridSM`
- `git fetch`
- `git rebase origin/ou-grid`
- `git push`

The rebase step will re-apply your recent commits on top of the `origin/ou-grid HEAD`. It will help keeping branches in sync. Ask me if you have any questions.

## LOCAL FILES

There are files that always differ between our branches (containing paths, conda env, etc..) I created "local" versions of these files and added them to .gitignore.
- `grid_search_local.py`
- `submit_batch_local.sh`

All the other stuff that includes (often changing) experiment name is in:
- `analysis/ou_tuning/workflow_local.py`
It is also local added to .gitignore.

Please find these three files in `/ddn/niknovikov19/repo/A1_OUinp`, copy them to your repo folder, and modify accordingly.

## WORKFLOW

You will routinely change two files:
- `grid_search_local.py` (experiment name)
- `analysis/ou_tuning/workflow_local.py` (grid creation and result processing)

In `analysis/ou_tuning/workflow_local.py`, the block of parameters you will change is in the beginning of the file:
- experiment name
- action flags (what to do)
- grid properties (for `need_create_grid=1`)

Action flags:
- need_create_grid: create `ou_grid.csv` file in the experiment config folder
- need_calc_result_table: collect sim results into `batch_result.csv` file in the exp result folder
- need_plot_rate_cv_grid: plot sim results (subfolder `plot` in the exp result folder)
- need_collect_trace_figures: copy voltage trace plots to `traces` subfolder of the exp result folder, give them meaningful names

A typical routine is:
- Create exp subfolder in `exp_configs`
- Copy `exp_cfg.py` and `batch_results.py` there (e.g. from `exp_configs/batch_i_ougrid_its4_20x20_med`)
- Modify `exp_cfg.py`
- Create `ou_grid.csv`: in `analysis/workflow_local.py`, set the exp name, grid properties, `need_create_grid=1` and other flags to 0, and run it.
- Set the experiment name in `grid_search_local.py`
- Run experiment (`qsub submit_batch_local.sh`)
- In `analysis/workflow_local.py`, set `need_create_grid=0` and other flags to 1 and run it again.

I usually run a preliminary experiment with 4x4 grid, and if it is ok - then a fine-grid experiment (usually 20x20).

I had troubles with running batchtools on some nodes, so I always submit it to node08:

`qsub -l hostname=node08 submit_batch_local.sh`

## EXPERIMENT TEMPLATE

As a template for OU-current experiment, you can take:
`exp_configs/batch_i_ougrid_its4_20x20_med`

Note that batch_params.py is updated to allow skipping of previously calculated jobs (if the batch crashed last time).

In `exp_cfg.py`, you will change `cfg.pops_active`. Also you may eventually want to change `cfg.duration`, `ncells_rec`, and  `ncells_plot`.

In the OU-current setup, `ou_mean` and `ou_std` are interpreted as percentages of `Gin * 70`. With this normalization, the ranges of interest are almost the same as in the OU-conductance setup (i.e. you can re-use old grid csv files).

## OU CURRENT IMPLEMENTATION

All the code related to OU stimulation is refactored, and the new file is `background_stim_new.py` (in replaces `BackgroundStim.py`)

In `BackgroundStim.py`, there was something, you should NEVER do: methods `addNoiseGClamp()` and `addNoiseIClamp()` are non-static (without `@staticmethod` decorator), but their first argument (`sim`) is treated not as an instance of addStim class (usually it has the name `self`) but as something else. These methods are called for a class, not for an instance (`addStim.addNoiseGClamp(sim)` instead of `x = addStim(); x.addNoiseGClamp(sim)`), so it works fine. But such usage is EXTREMELY unusual. If you write a method to be called for a class, you should use `@staticmethod` decorator.

Also, class names should begin from a capital letter (e.g. `AddStim`), see PEP8. But in our case, all the methods are static, so the class is not needed at all (see `background_stim_new.py`). 

In total, implementation of OU-current stimulation involves:
- `background_stim_new.py` (old `BackgroundStim.py`)
- `create_base_cfg.py` (analog of `cfg.py`)
- `create_net_params.py` (analog of `netParams.py`)
- `run_exp.py` (analog of `init.py`)
You can ask my help if you want to implement it in your main branch.


# Old

1. Choose a group of populations that you want to explore with the same grid. E.g., all SOM populations.

2. Create a subfolder in ***exp_configs/***, e.g. ***batch_ougrid_som_0***. This is referred to as "experiment name". The index 0 stands for the most coarse grid; maybe we will later refine it and run subsequent batches usind the indices 1, 2, etc.

3. Copy ***exp_cfg.py*** and ***batch_params.py*** from ***exp_configs/batch_ougrid_template/*** to your subfolder.

4. In ***exp_cfg.py***, list your populations in the `cfg.pops_active` field.

5. You can also modify other config paramters in ***exp_cfg.py***, e.g. `cfg.duration`. Note that ***exp_cfg.py*** settings are applied on top of the "default" config, defined in ***create_base_cfg.py***

6. Open ***analysis/ou_tuning/gen_regular_grid.py*** and define the grid properties and the experiment name. For example:
    ```
    # Define the ranges and number of points for the grid
    ou_mean_range = (0, 0.02)
    ou_mean_npoints = 4
    ou_std_range = (0, 0.008)
    ou_std_npoints = 3

    # Experiment name
    exp_name = 'batch_ougrid_som_0'
    ```

7. Run ***analysis/ou_tuning/gen_regular_grid.py***.
It will create a file ***ou_grid.csv*** in your experiment folder. It is a table with the columns **ou_mean** and **ou_std**; each row is a grid point.

8. Open ***grid_search.py***. Set the experiment name: `exp_name = 'batch_ougrid_som_0'`. 

9. In ***grid_search.py***, go to the `sge_config` variable, find the line `'conda activate netpyne_batch \n'`, and replace `netpyne_batch` by the name of your conda environment.
**Note:** your conda environment should contain **xarray** package.
You can also modify other `sge_config` settings.

10. Run ***grid_search.py***. It will run a batch, whose results will be stored in a subfolder of ***exp_results/*** with the name of your experiment, e.g. ***batch_ougrid_som_0***.

11. Open ***analysis/ou_tuning/create_bath_res_table.py*** and set the experiment name: `exp_name = 'batch_ougrid_som_0'`.

12. Run ***analysis/ou_tuning/create_bath_res_table.py***.
It will create a file ***batch_result.csv*** in your experiment result folder (***exp_results/batch_ougrid_som_0/***). This is a table with each row corresponding to a job of the batch.
The first two columns are **ou_mean** and **ou_std**. They are followed by the pairs of columns containing the firing rates and CVs for every population (e.g. **SOM2_r**, **SOM2_CV**, ...)

13.  Open ***analysis/ou_tuning/plot_rate_cv_grid.py*** and set the experiment name: `exp_name = 'batch_ougrid_som_0'`.
You can also change `t_limits` and `nspikes_min`, but please keep a record of the changes.

15. Run ***analysis/ou_tuning/plot_rate_cv_grid.py***.
It will create a subfolder ***plots*** in n your experiment result folder (***exp_results/batch_ougrid_som_0/***). It will contain a .png file for every population of your group.
