
import pandas as pd
from ppmi500.preprocessing import (
    fill_missing_data_json,
    fill_missing_data,
    get_nan_subids,
    add_qc_data,
    get_metadata_info
)

def main(dir):
    # Load data
    ids_df = pd.read_csv(dir + 'ppmi500_ids_date.csv')
    demo_df = pd.read_csv(dir + 'antspymm_v1pt2pt7_PPMI_Curated_Data_Cut_Public_20230612_rev_OR.csv')
    
    # Filter columns and manipulate data
    demo_df = demo_df[["subjectID", "filename", "age_BL","commonSex","duration_yrs","LEDD","moca",
                    "updrs1_score","updrs2_score","updrs3_score","updrs3_score_on","updrs4_score",
                    "updrs_totscore","updrs_totscore_on","joinedDX","AsynStatus","educ","race",
                    "tau","ptau", "abeta", "brainVolume"]]
    demo_df['date'] = demo_df['filename'].str.split('-').str[2]
    demo_df.drop(columns=['filename'], inplace=True)
    demo_df = convert_cols_to_string(demo_df, ['subjectID','date'])
    ids_df = convert_cols_to_string(ids_df, ['subjectID','date'])
    merged_df = pd.merge(ids_df, demo_df, how="left", on=['subjectID', 'date'])
    
    
    # Check for subids with missing DX, age, or sex info
    missing_dx_subids = get_nan_subids(merged_df, 'joinedDX')
    missing_age_subids = get_nan_subids(merged_df, 'age_BL')
    missing_sex_subids = get_nan_subids(merged_df, 'commonSex')
    print("Missing DX subids:", missing_dx_subids)
    print("Missing age: subids", missing_age_subids)
    print("Missing sex subids:", missing_sex_subids)


    # Fill missing sex info with data from JSON file
    merged_df = fill_missing_data_json(merged_df, 'PatientSex', 'commonSex')
    merged_df['commonSex'] = merged_df['commonSex'].replace({'M': 'Male'})

    # Fill missing age and research group data with metadata info
    metadata = get_metadata_info(dir)
    merged_df = convert_cols_to_string(merged_df, ['age_BL', 'joinedDX'])
    metadata = convert_cols_to_string(metadata, ['subjectAge', 'researchGroup'])
    merged_df = fill_missing_data(merged_df, metadata, 'age_BL', 'subjectAge')
    merged_df = fill_missing_data(merged_df, metadata, 'joinedDX', 'researchGroup')

    # Add QC data
    merged_df = add_qc_data(merged_df, dir)
    merged_df = merged_df.drop_duplicates()
    merged_df.to_csv(dir + 'PPMI500_demographic_QC.csv')

    # Check for subids with missing DX, age, or sex info
    missing_dx_subids = get_nan_subids(merged_df, 'joinedDX')
    missing_age_subids = get_nan_subids(merged_df, 'age_BL')
    missing_sex_subids = get_nan_subids(merged_df, 'commonSex')
    missing_qc = get_nan_subids(merged_df, 'has_humanqc')
    missing_modality = get_nan_subids(merged_df, 'modality')
    print("missing qc" , missing_qc)
    print("Missing DX subids:", missing_dx_subids)
    print("Missing age: subids", missing_age_subids)
    print("Missing sex subids:", missing_sex_subids)
    print("missing modality", missing_modality)


if __name__ == "__main__":
    main()

