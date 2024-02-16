# Identifying Modality From Raw DICOM Images
We can use the `SeriesDescription` field of the DICOM header to identify the modality of the image. The file `modality_map.csv` contains a `Description` column and a `cleaned_modality` column. Any image that has a `SeriesDescription` contained in
that `Description` field should be labeled with the corresponding modality in the `cleaned_modality` field.

< to-do: summary of how the scientists mapped the `SeriesDescription` column to the `cleaned_modality` >



# Converting a Image's Filepath to NRG Format
In order to determine the NRG-formatted filepath of an image, we need to know the following fields: 
- the project name
- the subject identifier
- the acquisition date of the image
- the (cleaned) modality of the image
- the series identifier of the image

The NRG formatted filename of the image would then be `<project>-<subject>-<acquisition-date>-<modality>-<image-filename>`.
Image filepaths are frequently represented in the format `<project>/<subject>/<acquisition-date>/<modality>/<series>/<project>-<subject>-<acquisition-date>-<modality>-<series>`.
If we want to denote additional processing that was performed on an image, we can concatenate a brief description-tag with the series ID in the NRG image's filename, i.e. for the brain-extracted image with series `100018` we can use `100018_brain_extraction` as the series identifier component of the filename
(But note: the NRG *directory path* should only include the series identifier itself).
