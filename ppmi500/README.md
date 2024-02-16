# ppmi500

ppmi500 is a Python package for preprocessing and analyzing data from the Parkinson's Progression Markers Initiative (PPMI). This package provides functionalities to handle missing data, fetch metadata, and perform quality control checks on PPMI datasets.

## Installation

You can install ppmi500 via pip:

```bash
pip install ppmi500
```


## Usage

Importing ppmi500

```python
import ppmi500
import pandas as pd

# you should have on hand the following files:
#  ppmi500 ids and dates
#  antspymm version of images
#  human qc 
merged = ppmi500.merge_qc_2_antspymm( ids_date, antspymm_version, human_qc )
# write it out ....
```

## Documentation

```python
help( ppmi500.functionname )
```
