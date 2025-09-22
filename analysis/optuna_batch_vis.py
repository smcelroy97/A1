import optuna
import os
import json
import pandas as pd

df = pd.read_csv('../simOutput/v45_optuna1/v45_optuna1.csv')

df = df[[col for col in df.columns if 'gain' not in col.lower()]]

# 2. Parse .out files and extract only hyperparameters (keys with 'gain')
out_dir = '../simOutput/v45_optuna1/out_files_v45_optuna1'
out_data = {}
for fname in os.listdir(out_dir):
    if fname.endswith('.out'):
        with open(os.path.join(out_dir, fname)) as f:
            data = json.load(f)
            sim_label = data.get('simLabel')
            if sim_label:
                # Only keep keys with 'gain' in the name
                hyperparams = {k: v for k, v in data.items() if 'gain' in k.lower()}
                out_data[sim_label] = hyperparams

# 3. Convert hyperparameters to DataFrame
hyper_df = pd.DataFrame.from_dict(out_data, orient='index')
hyper_df.reset_index(inplace=True)
hyper_df.rename(columns={'index': 'simLabel'}, inplace=True)

# 4. Merge, keeping only CSV data and hyperparameters
merged = df.merge(hyper_df, left_on='trial_label', right_on='simLabel', how='left')
merged.drop(columns=['simLabel'], inplace=True)

for col in ['...', 'IT6', 'CT6']:
    if col in merged.columns:
        merged.drop(columns=[col], inplace=True)

# Remove any unnamed index column
merged = merged.loc[:, ~merged.columns.str.contains('^Unnamed')]

merged.to_csv('../test_merged_results.csv', index=False)

# 5. Save or use merged DataFrame
merged.to_csv('../merged_results.csv', index=False)

params = {'EELayerGain.1': optuna.distributions.FloatDistribution(0.1, 5.0),
          'EELayerGain.2': optuna.distributions.FloatDistribution(0.1, 5.0),
          'EELayerGain.3': optuna.distributions.FloatDistribution(0.1, 5.0),
          'EELayerGain.4': optuna.distributions.FloatDistribution(0.1, 5.0),
          'EELayerGain.5A': optuna.distributions.FloatDistribution(0.1, 5.0),
          'EELayerGain.5B': optuna.distributions.FloatDistribution(0.1, 5.0),
          'EELayerGain.6': optuna.distributions.FloatDistribution(0.1, 5.0),
          'EILayerGain.1': optuna.distributions.FloatDistribution(0.1, 5.0),
          'EILayerGain.2': optuna.distributions.FloatDistribution(0.1, 5.0),
          'EILayerGain.3': optuna.distributions.FloatDistribution(0.1, 5.0),
          'EILayerGain.4': optuna.distributions.FloatDistribution(0.1, 5.0),
          'EILayerGain.5A': optuna.distributions.FloatDistribution(0.1, 5.0),
          'EILayerGain.5B': optuna.distributions.FloatDistribution(0.1, 5.0),
          'EILayerGain.6': optuna.distributions.FloatDistribution(0.1, 5.0),
          'IELayerGain.1': optuna.distributions.FloatDistribution(0.1, 5.0),
          'IELayerGain.2': optuna.distributions.FloatDistribution(0.1, 5.0),
          'IELayerGain.3': optuna.distributions.FloatDistribution(0.1, 5.0),
          'IELayerGain.4': optuna.distributions.FloatDistribution(0.1, 5.0),
          'IELayerGain.5A': optuna.distributions.FloatDistribution(0.1, 5.0),
          'IELayerGain.5B': optuna.distributions.FloatDistribution(0.1, 5.0),
          'IELayerGain.6': optuna.distributions.FloatDistribution(0.1, 5.0),
          'IILayerGain.1': optuna.distributions.FloatDistribution(0.1, 5.0),
          'IILayerGain.2': optuna.distributions.FloatDistribution(0.1, 5.0),
          'IILayerGain.3': optuna.distributions.FloatDistribution(0.1, 5.0),
          'IILayerGain.4': optuna.distributions.FloatDistribution(0.1, 5.0),
          'IILayerGain.5A': optuna.distributions.FloatDistribution(0.1, 5.0),
          'IILayerGain.5B': optuna.distributions.FloatDistribution(0.1, 5.0),
          'IILayerGain.6': optuna.distributions.FloatDistribution(0.1, 5.0)
          }


study = optuna.create_study(direction='minimize')

# Only keep hyperparameter columns for Optuna
hyperparam_keys = list(params.keys())

for _, row in merged.iterrows():
    trial = optuna.trial.create_trial(
        params={k: row[k] for k in hyperparam_keys if k in row},
        distributions=params,
        value=row['loss']
    )
    study.add_trial(trial)

optuna.visualization.plot_optimization_history(study).show()
