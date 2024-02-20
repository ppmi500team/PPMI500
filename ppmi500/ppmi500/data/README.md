# Identifying Modality From Raw DICOM Images
We can use the `SeriesDescription` field of the DICOM header to identify the modality of the image (CT, DAT, DTI, DTI_LR, DTI_RL, NM2DMT, PET, SPECT, T1w, T2Flair, rsfMRI, rsfMRI_LR, rsfMRI_RL, or Other). The file `modality_map.csv` contains a `Description` column and a `cleaned_modality` column. Any image that has a `SeriesDescription` contained in
that `Description` field should be labeled with the corresponding modality in the `cleaned_modality` field.

This modality mapping was created by our MRI scientists, who inferred the `cleaned_modalities` field based on the images' `SeriesDescriptions`.


# Converting a Image's Filepath to NRG Format
In order to determine the NRG-formatted filepath of an image, we need to know the following fields: 
- the project name, which is always just `PPMI`
- the subject identifier, which we pull out of the XML metadata that is downloaded with the PPMI dataset
- the acquisition date of the image, which is the `Acq Date` field pulled out of the metadata-records CSV that is downloaded with the PPMI dataset
- the (cleaned) modality of the image, which is pulled from the metadata-records CSV
- the series identifier of the image, which is pulled from the XML metadata

The NRG formatted filename of the image would then be `<project>-<subject>-<acquisition-date>-<modality>-<series-ID>-<image-filename>`.
Image filepaths are frequently represented in the format `<project>/<subject>/<acquisition-date>/<modality>/<series>/<project>-<subject>-<acquisition-date>-<modality>-<series-ID>`.
If we want to denote additional processing that was performed on an image, we can concatenate a brief description-tag with the series ID in the NRG image's filename, i.e. for the brain-extracted image with series `100018` we can use `100018_brain_extraction` as the series identifier component of the filename
(But note: the NRG *directory path* should only include the series identifier itself).

If you are running [dcm2niix](https://manpages.ubuntu.com/manpages/jammy/en/man1/dcm2niix.1.html) to perform the DICOM conversion to Nifti format, something similar to the following Python code should work

```
project    = 'PPMI'
subject_id = '1000001'
modality   = 'T2Flair'
acq_date   = '20230101'
image_id   = '123456'

input_dir = 'path/to/dicom/dir'

components   = [project, subject_id, acq_date, modality, image_id]
nrg_filename = '-'.join(components)
nrg_dirpath  = '/'.join(components)

os.makedirs(nrg_dirpath, exist_ok=True)

dcm2niix_cmd = f'dcm2niix -z y -o {nrg_dirpath} -f {nrg_filename} {input_dir}'
subprocess.run(dcm2niix_cmd, shell=True)
```

Also, the [antspymm Python module has a function](https://github.com/ANTsX/ANTsPyMM/blob/ba8deebd993b1a314ebe79dabf7e248132f6da8b/antspymm/mm.py#L913) `nrg_format_path()` that can be used to automatically create the NRG filepath.
