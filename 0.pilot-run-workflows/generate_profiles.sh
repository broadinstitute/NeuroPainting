#!/bin/bash
#
# NCP processing pipeline
# Shantanu Singh, 2019
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
BATCH_ID=NCP_PILOT_1
BUCKET=imaging-platform
MAXPROCS=3 # m4.xlarge has 4 cores; keep 1 free
mkdir -p ~/efs/${PROJECT_NAME}/workspace/
cd ~/efs/${PROJECT_NAME}/workspace/
mkdir -p log/${BATCH_ID}
PLATES=$(readlink -f ~/efs/${PROJECT_NAME}/workspace/scratch/${BATCH_ID}/plates_to_process.txt)

# Step 1.3 - Create an EBS temp directory for creating the backend
mkdir ~/ebs_tmp

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

# Copy config_files/config_CELLPAINTING.yml to cellpainting_scripts/config.yml (overwrite the existing file)
      
# Follow these steps verbatim
# https://cytomining.github.io/profiling-handbook/configure-tools-to-process-images.html#setup-distributed-cellprofiler

# Follow these steps verbatim -- can't do this just yet because we don't have a pipeline
# https://cytomining.github.io/profiling-handbook/setup-pipelines-and-images.html#get-cellprofiler-pipelines

# Specify pipeline set -- can't do this just yet because we don't have a pipeline
# PIPELINE_SET=cellpainting_ipsc_20x_phenix_with_bf_bin1_cp3/

# Follow these steps verbatim
# https://cytomining.github.io/profiling-handbook/setup-pipelines-and-images.html#prepare-images

# Create list of plates
mkdir -p scratch/${BATCH_ID}/
PLATES=$(readlink -f ~/efs/${PROJECT_NAME}/workspace/scratch/${BATCH_ID}/plates_to_process.txt)
echo "BR00106976" > ${PLATES}

# Follow these steps verbatim
# https://cytomining.github.io/profiling-handbook/setup-pipelines-and-images.html#create-loaddata-csvs

