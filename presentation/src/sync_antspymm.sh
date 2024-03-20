#!/bin/bash

# Check if less than 3 arguments are passed
if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <ID> <isSR> <output_dir> [exclusion_case]"
  echo "  ID: ID or unique identifier"
  echo "  indir: Should be  og ogsr pro  prosr"
  echo "  output_dir: Output directory path"
  echo "  exclusion_case: Optional. Specifies exclusion case (t1png, allpng, lotsanii, flairpriorWMH). If not specified, defaults are used."
  exit 1
fi


xx=$1        # The first argument: ID or unique identifier
isSR=$2      # The second argument: Should be either "true" or "false"
outdir=$3    # The third argument: Output directory path
exclusionCase=$4  # The fourth argument: Exclusion case (t1png, allpng, lotsanii)


case "$isSR" in
    og) src_directory="/mnt/cluster/data/PPMIBIG/nrgdata/data/PPMI/" ;;
    ogsr) src_directory="/mnt/cluster/data/PPMIBIG/nrgdatasr/data/PPMI/" ;;
    pro) src_directory="/mnt/cluster/data/PPMIBIG/processedCSV/PPMI/" ;;
    prosr) src_directory="/mnt/cluster/data/PPMIBIG/processedCSVSRFIRST/PPMI/" ;;
    *) echo "Invalid option. Please choose from 'og', 'ogsr', 'pro', or 'prosr'."; return 1;;
esac

# Base exclusions
declare -a baseExclusions=(
  '--exclude=*csv'
  '--exclude=*mat'
  '--exclude=*nii.gz'
  '--exclude=*trk'
  '--exclude=*DTI*'
  '--exclude=*rsfM*'
  '--exclude=*NM2D*'
)

# Default to base exclusions
declare -a exclusions=("${baseExclusions[@]}")

# Update exclusions based on the specified case
case $exclusionCase in
  "t1png")
    exclusions=(
      '--include="*/"'
      '--include="*brain.png"'
      '--exclude="*"'
    )
    ;;
  "allpng")
    exclusions=('--exclude=*.png')
    ;;
  "lotsanii")
    exclusions=(
      '--exclude=*nii.gz'
      '--exclude=*DTI*'
      '--exclude=*rsfM*'
    )
    ;;
  "flairpriorWMH")
    # First exclude everything, then include only flairpriorWMH.png files
    exclusions=(
      '--include="*/"'
      '--include="*flairpriorWMH.png"'
      '--exclude="*"'
    )
    ;;esac


exclusions=(
      '--include="*/"'
      '--include="*${exclusionCase}"'
      '--exclude="*"'
    )
echo "Starting the sync process with exclusion case: ${exclusionCase:-default}"

x=${src_directory}${xx}
# Determine the data path
echo "$isSR data selected for ID ${xx}."

echo "Source directory: ${x}"
echo "Destination directory: ${outdir}"

# Construct the rsync command with dynamic exclusions
rsyncCmd="rsync -av --progress -e 'ssh -i /Users/stnava/.aws/parallelcluster_20211103.pem' ${exclusions[@]} \"ubuntu@ec2-54-80-110-190.compute-1.amazonaws.com:${x}\" \"${outdir}\""

# Perform rsync
echo "Running rsync with the following command:"
echo $rsyncCmd
eval $rsyncCmd

echo "Sync process completed."
