import pickle
import pandas as pd
import os

# Directory containing OU mapping files
ou_mapping_dir = "/Users/scoot/A1ProjData/A1_sim_data/OU_mapping/"  # Update this to your folder path

# List all OU mapping files in the directory
ou_mapping_files = [os.path.join(ou_mapping_dir, f) for f in os.listdir(ou_mapping_dir) if f.endswith(".pkl")]

final_rate_dict = {}
final_isicv_dict = {}

for file in ou_mapping_files:
    with open(file, 'rb') as f:
        data = pickle.load(f)
        rate_dict = data["rate"]
        isicv_dict = data["isicv"]

        # Unpack rate_dict
        for pop, df in rate_dict.items():
            if pop not in final_rate_dict:
                final_rate_dict[pop] = df
            else:
                final_rate_dict[pop] = final_rate_dict[pop].combine_first(df)

        # Unpack isicv_dict
        for pop, df in isicv_dict.items():
            if pop not in final_isicv_dict:
                final_isicv_dict[pop] = df
            else:
                final_isicv_dict[pop] = final_isicv_dict[pop].combine_first(df)


# Save the merged results
save_path = os.path.join(ou_mapping_dir, "OUmapping_master.pkl")
with open(save_path, "wb") as f:
    pickle.dump({"rate": final_rate_dict, "isicv": final_isicv_dict}, f)

print(f"Merged results saved as {save_path}")