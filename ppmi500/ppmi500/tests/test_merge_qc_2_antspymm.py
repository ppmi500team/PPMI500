import ppmi500
import pandas as pd

dir = '' # Fill in dir 
antspymm_version = pd.read_csv(dir + 'antspymm_v1pt2pt7_PPMI_Curated_Data_Cut_Public_20230612_rev_OR.csv')
qc_df = pd.read_csv(dir + 'mergedhumanqc_full.csv')
metadata = pd.read_csv('../data/metadata.csv')
ids_df = pd.read_csv('../data/ppmi500_ids_date.csv') 
df = ppmi500.merge_qc_2_antspymm(ids_df, metadata, antspymm_version, qc_df)


## Check for missing data in important columns 
cols_to_check = ['commonSex', 'joinedDX', 'age_BL', 'modality', 'has_humanqc']
for col in cols_to_check : 
    missing_data = df[col].isna().sum()
    print(f"Missing data in {col} :", missing_data)


# Unique subject IDs
unique_subids = df['subjectID'].nunique()
print("Number of unique subject IDs:", unique_subids)

# Unique subject IDs with 'T1w' modality entry
unique_subids_with_T1w = df[df['modality'] == 'T1w']['subjectID'].nunique()
print("Number of unique subject IDs with 'T1w' as modality entry:", unique_subids_with_T1w)

# Modality counts
modality_counts = df['modality'].value_counts()
print("Counts of all modality types:", modality_counts)

# DX counts
df_dx = df[['subjectID', 'joinedDX']]
df_dx = df_dx.drop_duplicates()
dx_counts = df_dx['joinedDX'].value_counts()
print("Counts of all DX:", dx_counts)

# Make sure subid-date from original ids_df matches the output merged_df
ids_df['subid-date'] = ids_df['subjectID'].astype(str) + '-' + ids_df['date'].astype(str)
df['subid-date'] = df['subjectID'].astype(str) + '-' + df['date'].astype(str)
df1_subid_date_set = set(ids_df['subid-date'])
df2_subid_date_set = set(df['subid-date'])
# Check if sets match
if df1_subid_date_set == df2_subid_date_set:
    print("The 'subid-date' entries match between the two DataFrames.")
else:
    print("The 'subid-date' entries do not match between the two DataFrames.")
