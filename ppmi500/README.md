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
