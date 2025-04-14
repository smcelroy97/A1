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
