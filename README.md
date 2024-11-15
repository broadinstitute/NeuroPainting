# Unpacking the Biology of Psychiatric Genetics using Cell Painting

**Here, we propose to adapt the Cell Painting assay to interrogate traits in neuronal cells, and apply it to a cohort of 48 cell lines carrying the 22q11.2 deletion, a genetic variant strongly associated with psychiatric disease, to test the utility of neuronal Cell Painting in identifying disease relevant phenotypes in a high-throughput setting.**
Our work will bring together groups at the Imaging Platform and the Stanley Center to create a new strategy that could be integrated into multiple existing platforms at the Broad to enable, for the first time, the scaled investigation of neuronal profiles.
We anticipate that the workflows we will create will facilitate phenotypic screening of neurons at a scale that begins to match the transcriptional revolution, and constitute a key technology to help move from genetics to cellular phenotypes to actionable biology and mechanisms.
Gaining insight into neuronal morphology in health and disease will illuminate previously unknown aspects of neuronal biology, enable the interrogation of the effect of the hundreds of genetic risk variants on cellular phenotypes, and greatly complement several existing technologies pioneered at the Broad Institute such as CRISPR screens, drug screens, optical profiling and in situ sequencing to catalyze unprecedented discoveries that link genes and perturbations to neuronal phenotypes.

## Dataset summary

There are 48 IPSC lines available for this project from the [22q cohort](https://docs.google.com/spreadsheets/d/1ShXDddzO5mK7-C6G_BQYM3H7y8-2sGOOUn5uRX6SXVk/edit#gid=0):

| Metadata_line_source | Metadata_line_condition |  n |
|:---------------------|:------------------------|---:|
| human                | control                 | 22 |
| human                | deletion                | 22 |
| isogenic_control     | control                 |  2 |
| isogenic_deletion    | deletion                |  2 |

<details>
  <summary> Code </summary>

```r
read_tsv("metadata/NCP_STEM_1/platemap/BR_NCP_STEM_1.txt") %>%
  distinct(line_ID, line_condition, line_source) %>% count(line_source, line_condition) %>%
  knitr::kable()
```

</details>

TODO: All this information should be moved to the [Project Profiler airtable](https://airtable.com/appctUGldmRNkVS19/tblXX3mTxhCR9Bxbq/viwNJfGOOJot7Wr3x?blocks=hide).

TODO: Fill in information about number of features

| Experiment                   | Plate            | Features                                              | Magnification | Profiles                                                                                                                                              | Notes                                                                                                                                               |
|------------------------------|------------------|-------------------------------------------------------|---------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| NCP Stem 1                   | BR\_NCP\_STEM\_1 | Cell Painting (n=4293)                                | 20x           | [GitHub](1.run-workflows/profiles/NCP_STEM_1/BR_NCP_STEM_1)                                                                                           |                                                                                                                                                     |
| NCP Progenitor 1             | BR00127194       | Cell Painting (n=4295, includes 4 branching features) | 20x           | [GitHub](1.run-workflows/profiles/NCP_PROGENITORS_1/BR00127194)                                                                                       | This is a repeat of an experiment that failed ([notes)](https://github.com/broadinstitute/neuronal-cell-painting/issues/10#issuecomment-909397555). |
| NCP Neuron 1 - Cell Painting | BR00132672       |                                                       | 20x           | [S3](https://imaging-platform.s3.amazonaws.com/projects/2019_05_28_Neuronal_Cell_Painting/workspace/profiles/2022_03_03_NCP_NEURONS_2_20x/BR00132672) | ([notes](https://github.com/broadinstitute/neuronal-cell-painting/issues/21#issuecomment-1077803763))                                               |
| NCP Neuron 1 - Cell Painting | BR00132672       |                                                       | 63x           | [S3](https://imaging-platform.s3.amazonaws.com/projects/2019_05_28_Neuronal_Cell_Painting/workspace/profiles/2022_03_03_NCP_NEURONS_2_63x/BR00132672) | same ^^^                                                                                                                                            |
| NCP Neuron 1 - Cell Painting | BR00132673       |                                                       | 20x           | [S3](https://imaging-platform.s3.amazonaws.com/projects/2019_05_28_Neuronal_Cell_Painting/workspace/profiles/2022_03_03_NCP_NEURONS_2_20x/BR00132673) | same ^^^                                                                                                                                            |
| NCP Neuron 1 - Cell Painting | BR00132673       |                                                       | 63x           | [S3](https://imaging-platform.s3.amazonaws.com/projects/2019_05_28_Neuronal_Cell_Painting/workspace/profiles/2022_03_03_NCP_NEURONS_2_63x/BR00132673) | same ^^^                                                                                                                                            |

Failed experiments

| Experiment       | Plate                   | Features               | Profiles                                                                            | Notes                                                                                                                                         |
|------------------|-------------------------|------------------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| NCP Progenitor 1 | BR\_NCP\_PROGENITORS\_1 | Cell Painting (n=4293) | [GitHub](1.run-workflows/profiles/NCP_PROGENITORS_1/BR_NCP_PROGENITORS_1)           | This was the first attempt but it failed ([notes](https://github.com/broadinstitute/neuronal-cell-painting/issues/10#issuecomment-740777303)) |
|                  | BR\_NCP\_PROGENITORS\_1 | Branching (n=23)       | [GitHub](1.run-workflows/profiles/NCP_PROGENITORS_1_BRANCHING/BR_NCP_PROGENITORS_1) | Same as above, only branching metrics                                                                                                         |

Profiles from newer datasets (2022 onwards) are in this data repo <https://github.com/broadinstitute/2019_05_28_Neuronal_Cell_Painting>

We have RNA-Seq data (Nehme, Pietiläinen, et al., submitted) for 20 healthy controls and 28 patients with 22q deletion, across 3 stages:

- D0 (undifferentiated stem cells)
- D4 (progenitors, with GFP)
- D28 (neurons)

## Computational environment

### Python environment

We use [mamba](https://mamba.readthedocs.io/en/latest/) to manage the computational environment.

To install mamba see [instructions](https://mamba.readthedocs.io/en/latest/installation.html).

After installing mamba, execute the following to install and navigate to the environment:

```bash
# First, install the conda environment
mamba env create --force --file environment.yml

# If you had already installed this environment and now want to update it
mamba env update --file environment.yml --prune

# Then, activate the environment and you're all set!
environment_name=$(grep "name:" environment.yml | awk '{print $2}')
mamba activate $environment_name
```

### R

We use [`renv`](https://rstudio.github.io/renv/index.html) to reproduce R code.
We recommend using RStudio as your IDE.

Checkout this repository and then load the project `neuronal-cell-painting.Rproj` in RStudio.
You should see this

```text
# Bootstrapping renv 0.13.1 --------------------------------------------------
* Downloading renv 0.13.1 ... OK
* Installing renv 0.13.1 ... Done!
* Successfully installed and loaded renv 0.13.1.
* Project '~/Downloads/neuronal-cell-painting.Rproj' loaded. [renv 0.13.1]
* The project library is out of sync with the lockfile.
* Use `renv::restore()` to install packages recorded in the lockfile.
```

Now run `renv::restore()` and you're ready to run the R scripts in this repo.

Note: If you end up with issues with compiling libraries and you are on OSX, it's probably something to do with the macOS toolchain for versions of R starting at 4.y.z. being broken.
Follow these [instructions](https://thecoatlessprofessor.com/programming/cpp/r-compiler-tools-for-rcpp-on-macos/) to get set up.

#### Creating a new R notebook

<details>

Here's an example directory structure for a directory `<project>/<module-name>` containing an R notebook.
Note that R and Python notebooks can co-exist in the same directory

```text
<module-name>/
├── 0.knit-notebooks.R
├── 1.inspect-data.Rmd
├── _output.yaml
├── knit_notebooks
│   ├── 1.inspect-data.md
│   └── 1.inspect-data_files
```

Here are the steps to follow to create add such a notebook to this repo

- Create a stub for `1.inspect-data.Rmd`
- Copy [`_output.yaml`](https://gist.github.com/shntnu/12f5124fc0b8d9fbcef2765b89af9668) and [`0.knit-notebooks.R`](https://gist.github.com/shntnu/db9794e3d2ffbed09e290ffbb150512f) into the directory if it does not already exist
- Create a directory `knit_notebooks`; this is where the rendered versions of the notebooks will live
- Edit `0.knit-notebooks.R` to add `render_notebook("1.inspect-cp221")`, which will render this notebook in markdown int the `knit_notebooks` directory
- Now continue doing your analysis in `1.inspect-cp221.Rmd` and run things interactively as you would
- When its time to commit, generate the markdown for the notebook by running `0.knit-notebooks.R`. Ensure that your current working directory is the parent directory of `0.knit-notebooks.R` before doing so. As you add more notebooks to the directory, `0.knit-notebooks.R` will have more entries in it, but you may want to only render your latest notebook. In this case, you'd need to run things by hand: first run the function definition for `render_notebook()` and then run `render_notebook("1.inspect-data")`. This will render the file `1.inspect-data.md` along with the figures in `1.inspect-data_files`. You should commit all of this to the repo.
  
</details>

