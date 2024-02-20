def fill_missing_data_json(df, variable, df_col_name):
    """
    Fill missing data in DataFrame using JSON metadata.

    Parameters:
    - df (pandas.DataFrame): Input DataFrame.
    - variable (str): Variable to extract from JSON metadata.
    - df_col_name (str): Name of the column in the DataFrame to fill.

    Returns:
    pandas.DataFrame: DataFrame with missing values filled.
    """
    subid_list = get_nan_subids(df, df_col_name)
    missing_info = get_missing_json_data(subid_list, variable)
    merged_df = pop_missing_data(df, missing_info, df_col_name)
    return merged_df


def fill_missing_data(df, missing_info_df, df_col_name, info_col_name):
    """
    Fill missing data in DataFrame using information from another DataFrame.

    Parameters:
    - df (pandas.DataFrame): Input DataFrame.
    - missing_info_df (pandas.DataFrame): DataFrame containing missing information.
    - df_col_name (str): Name of the column in the DataFrame to fill.
    - info_col_name (str): Name of the column containing missing information.

    Returns:
    pandas.DataFrame: DataFrame with missing values filled.
    """
    subid_list = get_nan_subids(df, df_col_name)
    filtered_df = missing_info_df[missing_info_df['subjectIdentifier'].isin(subid_list)]
    filtered_df = filtered_df[['subjectIdentifier', info_col_name]]
    filtered_df.rename(columns={'subjectIdentifier': 'subjectID', info_col_name: df_col_name}, inplace=True)
    merged_df = pop_missing_data(df, filtered_df, df_col_name)
    return merged_df


def get_nan_subids(df, col_name):
    """
    Get a list of subject IDs with missing values in a specific column.

    Parameters:
    - df (pandas.DataFrame): Input DataFrame.
    - col_name (str): Name of the column to check for missing values.

    Returns:
    list: List of subject IDs with missing values.
    """
    nan_subids = []
    nan_subids.extend(df[df[col_name].isna()]['subjectID'])
    return list(set(nan_subids))


def get_missing_json_data(subid_list, variable):
    """
    Retrieve missing data from JSON metadata for a list of subject IDs.

    Parameters:
    - subid_list (list): List of subject IDs with missing data.
    - variable (str): Variable to extract from JSON metadata.

    Returns:
    pandas.DataFrame: DataFrame containing missing information.
    """
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



def convert_cols_to_string(df, col_names):
    """
    Convert columns in DataFrame to string type.

    Parameters:
    - df (pandas.DataFrame): Input DataFrame.
    - col_names (list): List of column names to convert to string.

    Returns:
    pandas.DataFrame: DataFrame with specified columns converted to string type.
    """
    for col_name in col_names:
        df[col_name] = df[col_name].astype(str)
    return df
    
    


def pop_missing_data(df, missing_info_df, df_col_name):
    """
    Populate missing data in DataFrame using information from another DataFrame.

    Parameters:
    - df (pandas.DataFrame): Input DataFrame.
    - missing_info_df (pandas.DataFrame): DataFrame containing missing information.
    - df_col_name (str): Name of the column in the DataFrame to fill.

    Returns:
    pandas.DataFrame: DataFrame with missing values filled.
    """
    merged_df = pd.merge(df, missing_info_df, how='left', on=['subjectID'], suffixes=('_df1', '_df2'))
    merged_df[df_col_name + '_df1'].fillna(merged_df[df_col_name + '_df2'], inplace=True)
    merged_df.rename(columns={df_col_name + '_df1': df_col_name}, inplace=True)
    merged_df.drop(columns=[df_col_name + '_df2'], inplace=True)
    return merged_df


def add_qc_data(qc, df):
    """
    Add quality control (QC) data to DataFrame.

    Parameters:
    - dir (str) : The directory path where the data files are located.
    - df (pandas.DataFrame): Input DataFrame.
    

    Returns:
    pandas.DataFrame: DataFrame with QC data added.
    """
    qc = qc[qc['has_humanqc'].isin(['1', 1])]
    qc.drop_duplicates(inplace=True)
    qc = convert_cols_to_string(qc, ['subjectID','date', 'has_humanqc'])
    df = convert_cols_to_string(df, ['subjectID','date'])
    merged_df = pd.merge(df, qc, how='left', on=['subjectID', 'date'])
    merged_df.drop_duplicates(inplace=True)
    return merged_df


def get_metadata_info():
    """
    Retrieve metadata information from S3 bucket.

    Returns:
    pandas.DataFrame: DataFrame containing metadata information.
    """
    s3 = boto3.client('s3')
    bucket_name = 'loni-data-curated-20230501'
    key = 'ppmi_500/curated/metadata/metadata.csv'
    # Read the CSV file from S3 into a DataFrame
    csv_obj = s3.get_object(Bucket=bucket_name, Key=key)
    csv_content = csv_obj['Body'].read().decode('utf-8')
    metadata = pd.read_csv(StringIO(csv_content))
    metadata = metadata[['subjectIdentifier', 'researchGroup', 'visitIdentifier', 'subjectAge']]
    metadata.drop_duplicates(inplace=True)
    metadata = metadata[metadata['visitIdentifier'] == 'Baseline']
    metadata.drop(columns=['visitIdentifier'], inplace=True)
    return metadata


def merge_qc_2_antspymm(ids_df, demo_df, qc):
    """
    Merge quality control (QC) data with demographic data for the PPMI 500 dataset.

    Parameters:
    - dir (str): The directory path where the data files are located.

    Returns:
    - pandas.DataFrame: The merged DataFrame containing demographic and QC data.

    This function loads demographic and QC data files, filters and manipulates columns,
    fills missing information for DX, age, sex, and QC data, and returns the merged DataFrame.

    """
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
    metadata = get_metadata_info()
    merged_df = convert_cols_to_string(merged_df, ['age_BL', 'joinedDX'])
    metadata = convert_cols_to_string(metadata, ['subjectAge', 'researchGroup'])
    merged_df = fill_missing_data(merged_df, metadata, 'age_BL', 'subjectAge')
    merged_df = fill_missing_data(merged_df, metadata, 'joinedDX', 'researchGroup')

    # Add QC data
    merged_df = add_qc_data(qc, merged_df)
    merged_df = merged_df.drop_duplicates()
    return merged_df



