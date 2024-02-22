# ppmi500

ppmi500 is a Python package for preprocessing and analyzing data from the Parkinson's Progression Markers Initiative (PPMI). This package provides functionalities to fill missing values, add quality control (QC) data, and merge demographic data with QC data.

## Installation

You can install ppmi500 via pip:

```bash
pip install ppmi500
```

## Usage 
Below are the available functions:\
		1. pop_missing_data(df, metadata, df_col_name): Populate missing data in a DataFrame (df) using information from another DataFrame (metadata).\
		2.  get_nan_subids(df, col_name): Get a list of subject IDs with missing values in a specific column.\
		3.  convert_cols_to_string(df, col_names): Convert columns in a DataFrame to string type.\
		4.  add_qc_data(qc, df): Add quality control (QC) data to a DataFrame.\
		5.  merge_qc_2_antspymm(ids_df, metadata, demo_df, qc): Merge quality control (QC) data with demographic data for the PPMI 500 dataset.

For detailed information on each function's parameters and return values, please refer to the docstrings provided within the code.


## Example

You should have on hand the following files:\
`antspymm_version` : antspymm version of images\
`human_qc` : file of human QC’d images

To merge the datasets containing demographic, QC, and other relevant information, you can use the `merge_qc_2_antspymm` function provided in the `ppmi500` module. This function takes four main inputs:
1. `ids_date`: This DataFrame contains subject IDs and dates, which are essential for matching records between datasets.
2. `metadata`: This DataFrame contains metadata with additional information about the subjects, such as age, sex, and diagnosis.
3. `antspymm_version`: This DataFrame contains the version of the ANTsPyMM dataset, which includes various neuroimaging and clinical data.
4. `human_qc`: This DataFrame contains quality control (QC) data, specifically information related to human QC checks.
ppmi500 ids_date and metadata files are located in ppmi500/data/
Here's how to use the function:

```python
import ppmi500
import pandas as pd
# load in antspymm_version
# load in human_qc 
metadata = pd.read_csv('../data/metadata.csv')
ids_df = pd.read_csv('../data/ppmi500_ids_date.csv') 
merged = ppmi500.merge_qc_2_antspymm(ids_date, metadata, antspymm_version, human_qc)
```

## Documentation

```python
help( ppmi500.functionname )
```


# Test Suite for PPMI 500 Dataset

This test suite contains a set of unit tests designed to verify the integrity and completeness of the PPMI 500 dataset. The tests cover various aspects such as unique subject IDs, missing data, gender counts, diagnostic label counts, modality counts, mean age, and quality control (QC) counts.

## Test Cases

1. **Unique Subject IDs**: Ensures that the number of unique subject IDs matches the expected value of 506.
2. **Missing Data**: Checks for missing data in critical columns including 'commonSex', 'joinedDX', 'age_BL', 'modality', and 'has_humanqc'. If any missing data is found, the test fails.
3. **Gender Counts**: Verifies that the counts of male and female subjects match the expected values (305 males, 201 females).
4. **Diagnostic Label Counts**: Validates the counts of subjects with specific diagnostic labels such as PD (224 expected), Prodromal (235 expected), and CN (48 expected).
5. **Modality Counts**: Checks the counts of subjects for each imaging modality, including rsfMRI (481 expected), NM2DMT (254 expected), DTI (419 expected), T1w (506 expected), and T2Flair (500 expected).
6. **Mean Age**: Verifies that the mean age of subjects matches the expected value of 65.8 years.
7. **Quality Control (QC) Counts**: Ensures that the counts of images passing QC (2642 expected) and failing QC (188 expected) match the expected values.

## Rationale

These tests are essential for ensuring the reliability and consistency of the dataset. They help identify any inconsistencies, missing data, or unexpected patterns that may indicate errors or issues in the dataset processing pipeline.

## Expectations

All tests should pass without any errors or failures. If a test fails, it indicates potential data integrity issues that need to be addressed. Any discrepancies between the expected and actual values should be investigated and resolved.

The test script (`test_merge_qc_2_antspymm.py`) containing these unit tests is located in the repository under the `tests` directory.

