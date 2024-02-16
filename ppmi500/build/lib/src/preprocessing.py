
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


def add_qc_data(df):
    """
    Add quality control (QC) data to DataFrame.

    Parameters:
    - df (pandas.DataFrame): Input DataFrame.

    Returns:
    pandas.DataFrame: DataFrame with QC data added.
    """
    qc = pd.read_csv(dir + 'mergedhumanqc_full.csv')
    qc = qc[qc['has_humanqc'].isin(['1', 1])]
    qc.drop_duplicates(inplace=True)
    qc = convert_cols_to_string(qc, ['subjectID','date', 'has_humanqc'])
    df = convert_cols_to_string(df, ['subjectID','date'])
    merged_df = pd.merge(df, qc, how='left', on=['subjectID', 'date'])
    merged_df.drop_duplicates(inplace=True)
    merged_df.to_csv('/Users/areardon/Desktop/x.csv')
    print(merged_df)
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
    s3.download_file(bucket_name, key, dir + 'metadata.csv')
    metadata = pd.read_csv(dir + 'metadata.csv')
    metadata = metadata[['subjectIdentifier', 'researchGroup', 'visitIdentifier', 'subjectAge']]
    metadata.drop_duplicates(inplace=True)
    metadata = metadata[metadata['visitIdentifier'] == 'Baseline']
    metadata.drop(columns=['visitIdentifier'], inplace=True)
    return metadata

