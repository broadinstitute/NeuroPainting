# Run profiling workflows on NCP Experiments

`../0.pilot-run-workflows/generate_profiles.sh` is used to produce profiles


Our goal with this module is to generate profiles for 308 stem cell lines.

There are 3 profiles files for each plate, stored in [profiles](https://github.com/broadinstitute/neuronal-cell-painting/tree/master/1.main-run-workflows/profiles), corresponding to different transformations of the data:

| file | description |
|-------------|---|
|augmented | mean profiles |
|count | cell counts |
|normalized | z-scored profiles |
|normalized_variable_selected | variable-selected z-scored profiles  |

The single cell SQLite files are available on S3:

|Metadata_Plate|
|:-------------|
| [BR_NCP_STEM_1](https://imaging-platform.s3.us-east-1.amazonaws.com/projects/2019_05_28_Neuronal_Cell_Painting/workspace/backend/NCP_STEM_1/BR_NCP_STEM_1/BR_NCP_STEM_1.sqlite) |


These are the counts of cell lines across the full dataset

|Metadata_Plate        |  n|
|:---------------------|--:|
|BR_NCP_STEM_1 | 48|


These are the details of batches - when they were imaged and the plate IDs of the constituent plates (a.k.a. `Metadata_Plate`)

| Fixation date | Batch ID | Metadata_Plate |
|:------------|----------| :-------|
| 2020-09-24 | NCP_STEM_1 | BR_NCP_STEM_1 |


## Instructions for adding Level 3,4a,4b CSV files, processed using `cytominer`, to this repo

The Level 3,4a,4b data were created using `cytominer`, by following the instructions `../0.pilot-run-workflows/generate_profiles.sh`.

Copy these files to `../../backend`

```sh
BATCH_ID=NCP_STEM_1
```

```sh
cd ~/work/projects/2019_05_28_Neuronal_Cell_Painting/workspace/

mkdir -p backend && cd backend && mkdir -p ${BATCH_ID} && cd ${BATCH_ID}

aws s3 sync --include "*.csv" --exclude "*.sqlite" s3://imaging-platform/projects/2019_05_28_Neuronal_Cell_Painting/workspace/backend/${BATCH_ID} .
```

Store this location as a variable

```sh
cd ~/work/projects/2019_05_28_Neuronal_Cell_Painting/workspace/software/neuronal-cell-painting/1.main-run-workflows/

external_backend_dir=../../../backend/${BATCH_ID}
```

We read these files in and save them out as `.gz` files after trimming the significant digits using `csv2gz.py`.

First optionally remove the existing `.gz` files

```sh
# list
find ${external_backend_dir} -type f -name "*.gz"

# remove
find ${external_backend_dir} -type f -name "*.gz" -exec rm {} \;
```

Gzip CSV files in place

```sh
pip install git+git://github.com/cytomining/pycytominer

find ${external_backend_dir} -type f -name "*.csv" -exec ./csv2gz.py {} \;
```

Sync them to this repo

```sh
rsync -arzv --include="*/" --include="*.gz" --exclude "*" ${external_backend_dir}/ profiles/
```

