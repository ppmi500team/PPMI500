import ppmi500
import unittest
import pandas as pd

dir = '' # Fill in local dir with location of antspymm_version and qc_df  
antspymm_version = pd.read_csv(dir + 'antspymm_v1pt2pt7_PPMI_Curated_Data_Cut_Public_20230612_rev_OR.csv')
qc_df = pd.read_csv(dir + 'mergedhumanqc_full.csv')
metadata = pd.read_csv('../ppmi500/data/metadata.csv')
ids_df = pd.read_csv('../ppmi500/data/ppmi500_ids_date.csv') 
df = ppmi500.merge_qc_2_antspymm(ids_df, metadata, antspymm_version, qc_df)


class TestSubjectIDsAndDataCompleteness(unittest.TestCase):
    def test_unique_subject_ids(self):
        unique_subids = df['subjectID'].nunique()
        expected_unique_subids = 506
        self.assertEqual(unique_subids, expected_unique_subids, 
                         f"Number of unique subject IDs is not as expected. Expected: {expected_unique_subids}, Actual: {unique_subids}")
        print("Test passed: Number of unique subject IDs matches the expected value.")


    def test_missing_data(self):
        cols_to_check = ['commonSex', 'joinedDX', 'age_BL', 'modality', 'has_humanqc']
        errors_found = False
        
        for col in cols_to_check:
            missing_data = df[col].isna().sum()
            if missing_data > 0:
                errors_found = True
                print(f"Error: Missing data in {col} : {missing_data}")
        self.assertFalse(errors_found, "Errors found: Missing data in one or more columns.")
        if not errors_found:
            print("Test passed: No missing data found in the specified columns.")

    def test_gender_counts(self):
        # Drop duplicate rows based on subjectID and commonSex
        unique_df = df.drop_duplicates(subset=['subjectID', 'commonSex'])
        sex_counts = unique_df['commonSex'].value_counts()
        expected_counts = {'Male': 305, 'Female': 201}
        self.assertEqual(sex_counts.to_dict(), expected_counts, "Gender counts do not match expected values.")
        print("Test passed: Gender counts match the expected values.")


    def test_joined_dx_counts(self):
        # Count the number of subjects for each joinedDX label
        pd_count = df[df['joinedDX'].str.contains('PD|Parkinson', case=False)]['subjectID'].nunique()
        prodromal_count = df[df['joinedDX'].str.contains('Prodromal', case=False)]['subjectID'].nunique()
        cn_count = df[df['joinedDX'].str.contains('CN', case=False)]['subjectID'].nunique()

        # Assert the expected counts
        self.assertEqual(pd_count, 224, "Expected 224 subjects with PD label")
        self.assertEqual(prodromal_count, 234, "Expected 234 subjects with Prodromal label")
        self.assertEqual(cn_count, 48, "Expected 48 subjects with CN label")
        print("Test passed: JoinedDX label counts match the expected values.")


    def test_modality_counts(self):
        rs_count = df[df['modality'].str.contains('rsfMRI', case=False)]['subjectID'].nunique()
        nm_count = df[df['modality'].str.contains('NM2DMT', case=False)]['subjectID'].nunique()
        dti_count = df[df['modality'].str.contains('DTI', case=False)]['subjectID'].nunique()
        t1w_count = df[df['modality'].str.contains('T1w', case=False)]['subjectID'].nunique()
        t2_count = df[df['modality'].str.contains('T2Flair', case=False)]['subjectID'].nunique()
        
        self.assertEqual(rs_count, 481, "Unexpected count for rsfMRI modality")
        self.assertEqual(nm_count, 254, "Unexpected count for NM2DMT modality")
        self.assertEqual(dti_count, 419, "Unexpected count for DTI modality")
        self.assertEqual(t1w_count, 506, "Unexpected count for T1w modality")
        self.assertEqual(t2_count, 500, "Unexpected count for T2Flair modality")
        print("Test passed: Modality counts match the expected values.")


    def test_mean_age(self):
        # Assuming 'df' is your DataFrame
        unique_df = df.drop_duplicates(subset=['subjectID'])
        mean_age = unique_df['age_BL'].mean()
        mean_age = round(mean_age,1)
        expected_mean_age = 65.8
        self.assertAlmostEqual(mean_age, expected_mean_age, places=1, 
                               msg=f"Mean age is not as expected. Expected: {expected_mean_age}, Actual: {mean_age}")
        print("Test passed: Mean age matches the expected value.")


    def test_qc_counts(self):
        # Assuming 'df' is your DataFrame containing the data
        qc_value_counts = df.drop_duplicates(subset=['subjectID', 'fn'])['all_humanqc_pass'].value_counts()
        expected_true_count = 2642
        expected_false_count = 188
        
        self.assertEqual(qc_value_counts[True], expected_true_count, 
                         f"Expected {expected_true_count} True values, but found {qc_value_counts[True]}")
        self.assertEqual(qc_value_counts[False], expected_false_count, 
                         f"Expected {expected_false_count} False values, but found {qc_value_counts[False]}")
        print("Test passed: Value counts for 'has_human_qc' match the expected values.")


if __name__ == '__main__':
    unittest.main()

    



