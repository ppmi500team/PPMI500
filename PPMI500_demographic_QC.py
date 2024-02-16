import pandas as pd
import boto3
import json

# Define directory where data is located
dir = '/Users/areardon/Desktop/Projects/PPMI_500/ground_truth_dataset/'

def main():
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
    demo_df['date'] = demo_df['date'].astype(str)
    ids_df['date'] = ids_df['date'].astype(str)
    merged_df = pd.merge(ids_df, demo_df, how="left", on=['subjectID', 'date'])
    
    
    # Check for subids wiht missing DX, age, or sex info
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
    metadata = get_metadata_info()
    merged_df = fill_missing_data(merged_df, metadata, 'age_BL', 'subjectAge')
    merged_df = fill_missing_data(merged_df, metadata, 'joinedDX', 'researchGroup')

    # Add QC data
    merged_df = add_qc_data(merged_df)
    merged_df.to_csv(dir + 'PPMI500_demographic_QC.csv')

    # Check for subids wiht missing DX, age, or sex info
    missing_dx_subids = get_nan_subids(merged_df, 'joinedDX')
    missing_age_subids = get_nan_subids(merged_df, 'age_BL')
    missing_sex_subids = get_nan_subids(merged_df, 'commonSex')
    print("Missing DX subids:", missing_dx_subids)
    print("Missing age: subids", missing_age_subids)
    print("Missing sex subids:", missing_sex_subids)



def fill_missing_data_json(df, variable, df_col_name):
    subid_list = get_nan_subids(df, df_col_name)
    missing_info = get_missing_json_data(subid_list, variable)
    merged_df = pop_missing_data(df, missing_info, df_col_name)
    return merged_df


def fill_missing_data(df, missing_info_df, df_col_name, info_col_name):
    subid_list = get_nan_subids(df, df_col_name)
    filtered_df = missing_info_df[missing_info_df['subjectIdentifier'].isin(subid_list)]
    filtered_df = filtered_df[['subjectIdentifier', info_col_name]]
    filtered_df.rename(columns={'subjectIdentifier': 'subjectID', info_col_name: df_col_name}, inplace=True)
    merged_df = pop_missing_data(df, filtered_df, df_col_name)
    return merged_df


def get_nan_subids(df, col_name):
    nan_subids = []
    nan_subids.extend(df[df[col_name].isna()]['subjectID'])
    return list(set(nan_subids))


def get_missing_json_data(subid_list, variable):
    bucket_name = 'loni-data-curated-20230501'
    prefix = 'ppmi_500/curated/data/PPMI/'
    s3 = boto3.client('s3')

    data = []

    for subid in subid_list:
        key_prefix = f"{prefix}{subid}/"
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=key_prefix)

        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                if key.endswith('.json'):
                    response = s3.get_object(Bucket=bucket_name, Key=key)
                    metadata = json.loads(response['Body'].read())
                    patient_info = metadata.get(variable, 'Unknown')
                    data.append({'subjectID': subid, 'commonSex': patient_info})
                    break

    df = pd.DataFrame(data)
    return df


def pop_missing_data(df, missing_info_df, df_col_name):
    merged_df = pd.merge(df, missing_info_df, how='left', on=['subjectID'], suffixes=('_df1', '_df2'))
    merged_df[df_col_name + '_df1'].fillna(merged_df[df_col_name + '_df2'], inplace=True)
    merged_df.rename(columns={df_col_name + '_df1': df_col_name}, inplace=True)
    merged_df.drop(columns=[df_col_name + '_df2'], inplace=True)
    return merged_df


def add_qc_data(df):
    qc = pd.read_csv(dir + 'mergedhumanqc_full.csv')
    qc['date'] = qc['date'].astype(str)
    df['date'] = df['date'].astype(str)
    merged_df = pd.merge(df, qc, how='left', on=['subjectID', 'date'])
    merged_df.drop_duplicates(inplace=True)
    return merged_df


def get_metadata_info():
    s3 = boto3.client('s3')
    bucket_name = 'loni-data-curated-20230501'
    key = 'ppmi_500/curated/metadata/metadata.csv'
    s3.download_file(bucket_name, key, dir + 'metadata.csv')
    metadata = pd.read_csv(dir + 'metadata.csv')
    metadata = metadata[['subjectIdentifier', 'researchGroup', 'visitIdentifier', 'subjectAge']]
    metadata.drop_duplicates(inplace=True)
    metadata = metadata[metadata['visitIdentifier'] == 'Baseline']
    metadata.drop(columns=['visitIdentifier'], inplace=True)
    return metadata


if __name__ == "__main__":
    main()
