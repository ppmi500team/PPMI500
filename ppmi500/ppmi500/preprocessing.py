import pandas as pd

def process_qc_data(df_AR_path, df_LF_path, df_XW_path, df_BA_path):
    """
    Processes Quality Control (QC) data from multiple CSV files containing QC information from different sources. It concatenates the data, filters and reorders the columns, converts certain string values to boolean, and removes duplicate rows.
    
    ## Parameters:
    - df_AR_path: String. File path of the CSV file containing QC data from source 'AR'.
    - df_LF_path: String. File path of the CSV file containing QC data from source 'LF'.
    - df_XW_path: String. File path of the CSV file containing QC data from source 'XW'.
    - df_BA_path: String. File path of the CSV file containing QC data from source 'BA'.
    
    ## Returns:
    - df: Pandas DataFrame. Preprocessed DataFrame containing concatenated and cleaned QC data from all sources.
    """
    
    # Read the dataframes
    df_AR = pd.read_csv(df_AR_path)
    df_LF = pd.read_csv(df_LF_path)
    df_XW = pd.read_csv(df_XW_path)
    df_BA = pd.read_csv(df_BA_path)

    # Concatenate the dataframes
    df = pd.concat([df_AR, df_LF, df_XW, df_BA], ignore_index=True)

    # Define the desired column order
    desired_order = [
        'subjectID', 'date', 'imageID', 'modality', 'qcfail_orientation', 'qcfail_wrong_modality',
        'qcfail_phantom', 'qcfail_spacing', 'qcfail_intensity_saturation', 'qcfail_background_noise',
        'qcfail_motion', 'qcfail_signal_dropout', 'qcfail_temporal_noise', 'qcfail_insufficient_volumes',
        'qcfail_FOV', 'qcfail_other', 'qchuman_DTI_AR', 'qchuman_FLAIR_XUE', 'qchuman_T1w_XUE',
        'qchuman_DTI_LF', 'qchuman_rsfMRI_LF', 'qchuman_FLAIR_BA', 'qchuman_T1w_BA', 'qchuman_NM_BA', 'has_humanqc', 'siteKey'
    ]

    # Filter columns and reorder
    df = df.filter(regex='^(?!Unnamed)').reindex(columns=desired_order)

    # Define mapping of string values to boolean
    str_to_bool = {'TRUE': True, 'FALSE': False, 'PASS': True, 'FAIL': False, 'True': True, 'False': False}
    
    # Columns to convert from string to boolean
    cols = ['qchuman_DTI_AR', 'qchuman_FLAIR_XUE', 'qchuman_T1w_XUE', 'qchuman_DTI_LF', 'qchuman_rsfMRI_LF']

    # Function to convert strings to boolean values
    def convert_to_bool(value):
        if isinstance(value, str):
            value = value.strip().upper()  # Remove leading/trailing spaces and convert to uppercase
            return str_to_bool.get(value, None)
        return value

    # Convert strings to boolean values
    for col in cols:
        df[col] = df[col].apply(convert_to_bool)

    # Remove duplicate rows
    df.drop_duplicates(inplace=True)
    return df



def pop_missing_data(df, metadata, df_col_name):
    """
    Fill missing data in DataFrame using information from another DataFrame.

    Parameters:
    - df (pandas.DataFrame): Input DataFrame.
    - metadata (pandas.DataFrame): DataFrame containing missing information.
    - df_col_name (str): Name of the column in the DataFrame to fill.

    Returns:
    pandas.DataFrame: DataFrame with missing values filled.
    """
    subid_list = get_nan_subids(df, df_col_name)
    metadata['subjectID'] = metadata['subjectID'].astype(str)
    filtered_df = metadata[metadata['subjectID'].isin(subid_list)]
    filtered_df = filtered_df[['subjectID', df_col_name]]
    merged_df = pd.merge(df, filtered_df, how='left', on=['subjectID'], suffixes=('_df1', '_df2'))
    merged_df[df_col_name + '_df1'].fillna(merged_df[df_col_name + '_df2'], inplace=True)
    merged_df.rename(columns={df_col_name + '_df1': df_col_name}, inplace=True)
    merged_df.drop(columns=[df_col_name + '_df2'], inplace=True)
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


def add_qc_data(qc, df):
    """
    Add quality control (QC) data to DataFrame.
    
    Parameters:
    - qc (pandas.DataFrame): DataFrame containing quality control data.
    - df (pandas.DataFrame): Input DataFrame.

    Returns:
    pandas.DataFrame: DataFrame with QC data added.

    This function takes two DataFrames as input: qc and df. It filters the QC data, converts columns to string type, merges the QC data with the input DataFrame based on subject ID and date, and returns the merged DataFrame with QC data added.
    """
    qc = qc[qc['has_humanqc'].isin(['1', 1])]
    qc.drop_duplicates(inplace=True)
    qc = convert_cols_to_string(qc, ['subjectID','date', 'has_humanqc'])
    df = convert_cols_to_string(df, ['subjectID','date'])
    merged_df = pd.merge(df, qc, how='left', on=['subjectID', 'date'])
    merged_df.drop_duplicates(inplace=True)
    return merged_df


def merge_qc_2_antspymm(ids_df, metadata, demo_df, qc):
    """
    Merge quality control (QC) data with demographic data for the PPMI 500 dataset.

    Parameters:
    - ids_df (pandas.DataFrame): DataFrame containing subject IDs and dates.
    - demo_df (pandas.DataFrame): DataFrame containing demographic data.
    - qc (pandas.DataFrame): DataFrame containing quality control data.

    Returns:
    pandas.DataFrame: The merged DataFrame containing demographic and QC data.
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

    # Fill missing age and research group data with metadata info
    merged_df = pop_missing_data(merged_df, metadata, 'age_BL')
    merged_df = pop_missing_data(merged_df, metadata, 'joinedDX')
    merged_df = pop_missing_data(merged_df, metadata, 'commonSex')

    # Add QC data
    merged_df = add_qc_data(qc, merged_df)
    merged_df = merged_df.drop_duplicates()
    return merged_df
