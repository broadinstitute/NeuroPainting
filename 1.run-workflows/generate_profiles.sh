#!/bin/bash
#
# NCP processing pipeline
# Gregory Way, 2019 (adapted by Shantanu Singh)
#
# Instructions to generate cell painting profiles for the NCP pilot experiments
# Pipeline generated using the profiling handbook:
#     https://cytomining.github.io/profiling-handbook/

############################
# Step 1 - Configure the Environment
############################
# Step 1.1: Setup a virtual machine on AWS
#
#     * Launch an ec2 instance on AWS
#     * AMI: cytomining/images/hvm-ssd/cytominer-ubuntu-trusty-14.04-amd64-server-1529668435
#     * Instance Type: m4.xlarge
#     * Network: vpc-35149752 - Subnet: subnet-55625c0d (cellpainting_1b)
#     * IAM role: `s3-imaging-platform-role
#     * Add New Volume (if necessary): `EBS` with 110 GiB
#     * No Tags
#     * Select Existing Security Group: `SSH_HTTP`
#     * Review and Launch
#     * ssh -i <USER>.pem ubuntu@<Public DNS IPv4>
#     * Inside AWS terminal: `aws configure` and input security credentials
#
# See https://cytomining.github.io/profiling-handbook/configure-environment.html#set-up-a-virtual-machine
# for more details

# Step 1.2: Define Variables
PROJECT_NAME=2019_05_28_Neuronal_Cell_Painting
BATCH_ID=NCP_STEM_1
SAMPLE_FULL_PLATE_NAME=BR_NCP_STEM_1
BUCKET=imaging-platform
MAXPROCS=3 # m4.xlarge has 4 cores; keep 1 free
mkdir -p ~/efs/${PROJECT_NAME}/workspace/
cd ~/efs/${PROJECT_NAME}/workspace/
mkdir -p log/${BATCH_ID}

# the scripts were run verbatim for these  additional batches with appropriate modifications to
# SAMPLE_PLATE_ID and contents of $PLATES
#BATCH_ID=NCP_PILOT_3
#SAMPLE_FULL_PLATE_NAME=BR_NCP_PILOT_3
#BATCH_ID=NCP_PILOT_3B
#SAMPLE_FULL_PLATE_NAME=MAtt_ICC_test

# Step 1.3 - Create an EBS temp directory for creating the backend
mkdir -p ~/ebs_tmp

############################
# Step 2 - Configure Tools to Process Images
############################
cd ~/efs/${PROJECT_NAME}/workspace/
mkdir -p software
cd software

# check whether the repos below already exist
# If they do, run `git status` to make sure that the files haven't been modified
# If they don't exist then clone as below
git clone git@github.com:broadinstitute/cellpainting_scripts.git
git clone git@github.com:broadinstitute/pe2loaddata.git
git clone git@github.com:broadinstitute/cytominer_scripts.git
git clone git@github.com:CellProfiler/Distributed-CellProfiler.git

# Copy config_files/config.yml to cellpainting_scripts/ (overwrite the existing file)

# Follow these steps verbatim
# https://cytomining.github.io/profiling-handbook/configure-tools-to-process-images.html#update-some-packages
# https://cytomining.github.io/profiling-handbook/configure-tools-to-process-images.html#setup-distributed-cellprofiler
# https://cytomining.github.io/profiling-handbook/setup-pipelines-and-images.html#get-cellprofiler-pipelines

# Specify pipeline set
PIPELINE_SET=cellpainting_ipsc_20x_phenix_with_bf_bin1_cp3/
#PIPELINE_SET=cellpainting_ipsc_20x_phenix_with_bf_bin1_cp3/

# NOTE:The actual version of the pipeline run was this:
# https://github.com/broadinstitute/imaging-platform-pipelines/pull/17/commits/1c3ed24cffc042195e01b6bd791353a2f75fc450
# which differs from the master branch only in the way the outputs are stored.

# Follow these steps verbatim
# https://cytomining.github.io/profiling-handbook/setup-pipelines-and-images.html#prepare-images

# Create list of plates
mkdir -p scratch/${BATCH_ID}/
PLATES=$(readlink -f ~/efs/${PROJECT_NAME}/workspace/scratch/${BATCH_ID}/plates_to_process.txt)
echo "BR_NCP_STEM_1"|tr " " "\n" > ${PLATES}
#echo "BR_NCP_PILOT_3"|tr " " "\n" > ${PLATES}
#echo "MAtt_ICC_test"|tr " " "\n" > ${PLATES}

# Follow these steps verbatim
# https://cytomining.github.io/profiling-handbook/setup-pipelines-and-images.html#create-loaddata-csvs
# Note:
# - the cellpainting_scripts/config.ini file had not been set up correctly, and pe2loaddata got stuck
# so I did it by hand (i.e. `parallel --dry-run` and then run each command)
# - pe2loaddata has been recently updated but there are no instructions for install or use.
# I thus checked out an old commit
# cd ~/efs/2019_05_28_Neuronal_Cell_Painting/workspace/software/pe2loaddata
# git checkout 62b5e35647d2b6e7fafab4ae4b189b4f2cfecdad

# Follow these steps verbatim
# https://cytomining.github.io/profiling-handbook/setup-jobs.html#illumination-correction
# https://cytomining.github.io/profiling-handbook/setup-jobs.html#analysis
# but change the docker image for both
# `--cp_docker_image cellprofiler/cellprofiler:3.1.8`
# This errored but the config files got created without a hitch. See https://github.com/broadinstitute/cmQTL/issues/14#issuecomment-505551405

# Copy the `dcp_config_files` directory to `cellpainting_scripts`
cp ../neuronal-cell-painting/0.pilot-run-workflows/dcp_config_files/* ../cellpainting_scripts/dcp_config_files/

# Follow these steps verbatim
# https://cytomining.github.io/profiling-handbook/run-jobs.html#run-illum-dcp
# https://cytomining.github.io/profiling-handbook/run-jobs.html#dcp
# https://cytomining.github.io/profiling-handbook/create-profiles.html#create-database-backend


############################
# Step 2B - Aggregate for plates that don't have standard compartments
############################

# First install cytomining/cytotools
# In R:
# devtools::install_github("cytomining/cytotools")
# After installing this package, run the snippet below, and add the output to your PATH:
# library(cytotools)
# normalizePath(file.path(path.package("cytotools"), "scripts"))

# Run this https://cytomining.github.io/profiling-handbook/create-profiles.html#create-database-backend
# before do the following before running `collate.R`

cd  ~/ebs_tmp/${PROJECT_NAME}/workspace/software/cytominer_scripts

cp collate.R collate_neurons.R

# Now edit the line
# aggregate_cmd <- paste("./aggregate.R", cache_backend_file, "-o", cache_aggregated_file)
# to
# aggregate_cmd <- paste("/home/ubuntu/R/library/cytotools/scripts/cytotools_aggregate", cache_backend_file, "-c", "CellBodies,CellBodiesPlusNeurites,Cytoplasm,Nuclei,Neurites", "-t", "Image", "-o", cache_aggregated_file)
# or, for neurons with antibody staining, also add PrelimNuclei
# aggregate_cmd <- paste("/home/ubuntu/R/library/cytotools/scripts/cytotools_aggregate", cache_backend_file, "-c", "CellBodies,CellBodiesPlusNeurites,Cytoplasm,Nuclei,Neurites,PrelimNuclei", "-t", "Image", "-o", cache_aggregated_file)
# and then run the collate step, but replace `./collate.R` with `./collate_neurons.R`

############################
# Step 3 - Annotate
############################
# NOTE - The annotate step creates `augmented` profiles in the `backend` folder
# `augmented` profiles represent aggregated per-well data annotated with metadata
# Follow this step with some modifications (see below)
# https://cytomining.github.io/profiling-handbook/create-profiles.html#annotate

# Retrieve metadata information
aws s3 sync s3://${BUCKET}/projects/${PROJECT_NAME}/workspace/metadata/${BATCH_ID}/ ~/efs/${PROJECT_NAME}/workspace/metadata/${BATCH_ID}/

# Use cytotools to run annotation
cd  ~/efs/${PROJECT_NAME}/workspace/software/cytominer_scripts

parallel \
  --no-run-if-empty \
  --eta \
  --joblog ../../log/${BATCH_ID}/annotate.log \
  --results ../../log/${BATCH_ID}/annotate \
  --files \
  --keep-order \
  /home/ubuntu/R/library/cytotools/scripts/cytotools_annotate \
  --workspace_directory ../../ \
  --batch_id ${BATCH_ID} \
  --plate_id {1} :::: ${PLATES}

############################
# Step 4 - Normalize
############################
# Note - The normalize step creates `normalized` profiles in the `backend` folder
# The step z-scores each feature using all wells (i.e. use all "non-dummy" wells)

# Follow this step with some modifications (see below)
# https://cytomining.github.io/profiling-handbook/create-profiles.html#normalize

# for neurons
compartments=CellBodies,CellBodiesPlusNeurites,Cytoplasm,Nuclei,Neurites

# for neurons with antibody staining
compartments=CellBodies,CellBodiesPlusNeurites,Cytoplasm,Nuclei,Neurites,PrelimNuclei

# for regular cells (need to verify)
compartments=cells,cytoplasm,nuclei

parallel \
  --no-run-if-empty \
  --eta \
  --joblog ../../log/${BATCH_ID}/normalize.log \
  --results ../../log/${BATCH_ID}/normalize \
  --files \
  --keep-order \
  /home/ubuntu/R/library/cytotools/scripts/cytotools_normalize \
  --batch_id ${BATCH_ID} \
  --workspace_dir ../../ \
  --compartments ${compartments} \
  --plate_id {1} :::: ${PLATES}

############################
# Step 5 - Variable Selection
############################
# Follow this step with some modifications (no replicate correlation step; see below)
# https://cytomining.github.io/profiling-handbook/create-profiles.html#select-variables

# Note - Variable selection uses both normalized and unnormalized data
mkdir -p ../../parameters/${BATCH_ID}/sample/

# In the sampling steps below, we specify replicates = 1 because there is only 1
# replicate plate per platemap. Currently, sampling replicates within a plate is
# not supported in cytominer_scripts

# For neurons, first modify preselect.R so that compartments are handled correctly

# Replace occurences of
# stringr::str_subset("^Nuclei_|^Cells_|^Cytoplasm_")
# with
# stringr::str_subset("^Metadata_", negate = TRUE)

# This works for non-neurons too

# Step 5.0 - Sample normalized and unnormalized data
# Normalized
./sample.R \
  --batch_id ${BATCH_ID} \
  --pattern "_normalized.csv$" \
  --replicates 1 \
  --output ../../parameters/${BATCH_ID}/sample/${BATCH_ID}_normalized_sample.feather

# Unnormalized
./sample.R \
  --batch_id ${BATCH_ID} \
  --pattern "_augmented.csv$" \
  --replicates 1 \
  --output ../../parameters/${BATCH_ID}/sample/${BATCH_ID}_augmented_sample.feather

# Using the sampled feather files, perform a series of three variable selection steps
# Step 5.1 - Remove variables that have high correlations with other variables

./preselect.R \
  --batch_id ${BATCH_ID} \
  --input ../../parameters/${BATCH_ID}/sample/${BATCH_ID}_normalized_sample.feather \
  --operations correlation_threshold

# Step 5.2 - Remove variables that have low variance
./preselect.R \
  --batch_id ${BATCH_ID} \
  --input ../../parameters/${BATCH_ID}/sample/${BATCH_ID}_augmented_sample.feather \
  --operations variance_threshold

# Step 5.3 - Remove features known to be noisy
#SAMPLE_PLATE_ID='BR_NCP_STEM_1'
#SAMPLE_PLATE_ID='BR_NCP_PILOT_3'
SAMPLE_PLATE_ID='MAtt_ICC_test'
echo "variable" > ../../parameters/${BATCH_ID}/variable_selection/manual.txt

head -1 \
  ../../backend/${BATCH_ID}/${SAMPLE_PLATE_ID}/${SAMPLE_PLATE_ID}.csv \
  |tr "," "\n"|grep -v Meta|grep -E -v 'Granularity_14|Granularity_15|Granularity_16|Manders|RWC' >> \
  ../../parameters/${BATCH_ID}/variable_selection/manual.txt

# Step 5.4 - Apply the variable selection steps to the profiles
# Note - This creates the _normalized_variable_selected.csv files in `backend`

# For neurons, first modify select.R so that compartments are handled correctly

# Edit the code so that variables is created after metadata
#
# metadata <-
#   colnames(df) %>%
#   stringr::str_subset("^Metadata_")
#
# variables <-
#   setdiff(colnames(df), metadata)

# This works for non-neurons too

parallel \
  --no-run-if-empty \
  --eta \
  --joblog ../../log/${BATCH_ID}/select.log \
  --results ../../log/${BATCH_ID}/select \
  --files \
  --keep-order \
  ./select.R \
  --batch_id ${BATCH_ID} \
  --plate_id {1} \
  --filters variance_threshold,correlation_threshold,manual :::: ${PLATES}

############################
# Compute cell counts
############################

# If jumping in directly to this step, define BATCH_ID and PLATES
# PROJECT_NAME=2019_05_28_Neuronal_Cell_Painting
# BATCH_ID=NCP_STEM_1
# PLATES=$(readlink -f ~/efs/${PROJECT_NAME}/workspace/scratch/${BATCH_ID}/plates_to_process.txt)

cd ~/efs/${PROJECT_NAME}/workspace/software/cytominer_scripts

mkdir -p ~/ebs_tmp/${PROJECT_NAME}/workspace/backend/${BATCH_ID}

parallel \
  --no-run-if-empty \
  --eta \
  aws s3 sync \
  --exclude '"*"' \
  --include '"*.sqlite"' \
  s3://imaging-platform/projects/${PROJECT_NAME}/workspace/backend/${BATCH_ID}/{1}/ \
  ~/ebs_tmp/${PROJECT_NAME}/workspace/backend/${BATCH_ID}/{1}/ \
  :::: ${PLATES}


# create a file stats_neurons.R with these diffs
# diff stats.R stats_neurons.R
# < stats <- tbl(src = db, "image") %>%
# <   select(Metadata_Plate, Metadata_Well, Count_Cells) %>%
# ---
# > stats <- tbl(src = db, "Image") %>%
# >   select(Metadata_Plate, Metadata_Well, Count_Nuclei) %>%
# 27c27
# <   summarize(Count_Cells = sum(Count_Cells)) %>%
# ---
# >   summarize(Count_Nuclei = sum(Count_Nuclei)) %>%


# cell counts
parallel \
  --no-run-if-empty \
  --max-procs 1 \
  --joblog ../../log/${BATCH_ID}/stats.log \
  --results ../../log/${BATCH_ID}/stats \
  --files \
  --keep-order \
  --eta \
  ./stats_neurons.R  \
  ~/ebs_tmp/${PROJECT_NAME}/workspace/backend/${BATCH_ID}/{1}/{1}.sqlite \
  -o ../../backend/${BATCH_ID}/{1}/{1}_count.csv \
  :::: ${PLATES}

# check rows
parallel \
  --no-run-if-empty \
  --keep-order \
  wc -l ../../backend/${BATCH_ID}/{1}/{1}_count.csv :::: \
  ${PLATES}

# remove sqlite
parallel \
  --no-run-if-empty \
  --eta \
  rm ~/ebs_tmp/${PROJECT_NAME}/workspace/backend/${BATCH_ID}/{1}/{1}.sqlite \
  :::: ${PLATES}

############################
# Step 6 - Audit
############################

# Audit for replicate reproducibility
# https://cytomining.github.io/profiling-handbook/create-profiles.html#audit

PLATE_MAPS=../../scratch/${BATCH_ID}/plate_maps.txt

csvcut -c Plate_Map_Name \
  ../../metadata/${BATCH_ID}/barcode_platemap.csv | \
  tail -n +2|sort|uniq > \
  ${PLATE_MAPS}

mkdir -p ../../audit/${BATCH_ID}/

# for NCP_STEM_1
replicate_grouping_variables=Metadata_Plate_Map_Name,Metadata_line_ID,Metadata_plating_density

# for NCP_PILOT_3
replicate_grouping_variables=Metadata_Plate_Map_Name,Metadata_line_condition,Metadata_compound_ID,Metadata_plating_density

# for NCP_PILOT_3B
replicate_grouping_variables=Metadata_Plate_Map_Name,Metadata_line_condition,Metadata_plating_density

parallel \
  --no-run-if-empty \
  --eta \
  --joblog ../../log/${BATCH_ID}/audit.log \
  --results ../../log/${BATCH_ID}/audit \
  --files \
  --keep-order \
  ./audit.R \
  -b ${BATCH_ID} \
  -m {1} \
  -f _normalized_variable_selected.csv \
  -o ../../audit/${BATCH_ID}/{1}_audit.csv \
  -l ../../audit/${BATCH_ID}/{1}_audit_detailed.csv \
  -p ${replicate_grouping_variables} :::: ${PLATE_MAPS}

############################
# Step 6 - Convert to other formats
############################

# Follow only the first part of this step
# https://cytomining.github.io/profiling-handbook/create-profiles.html#convert-to-other-formats
# i.e.:

parallel \
  --no-run-if-empty \
  --eta \
  --joblog ../../log/${BATCH_ID}/csv2gct_backend.log \
  --results ../../log/${BATCH_ID}/csv2gct_backend \
  --files \
  --keep-order \
  ./csv2gct.R \
  ../../backend/${BATCH_ID}/{1}/{1}_{2}.csv \
  -o ../../backend/${BATCH_ID}/{1}/{1}_{2}.gct :::: ${PLATES} ::: augmented normalized normalized_variable_selected

############################
# Step 7 - Upload data
############################

# Follow this step nearly verbatim
# https://cytomining.github.io/profiling-handbook/create-profiles.html#upload-data

parallel \
  aws s3 sync \
  ../../{1}/${BATCH_ID}/ \
  s3://${BUCKET}/projects/${PROJECT_NAME}/workspace/{1}/${BATCH_ID}/ ::: audit backend batchfiles load_data_csv log metadata parameters scratch
