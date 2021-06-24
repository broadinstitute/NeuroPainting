# Unpacking the Biology of Psychiatric Genetics using Cell Painting


**Here, we propose to adapt the Cell Painting assay to interrogate traits in neuronal cells, and apply it to a cohort of 48 cell lines carrying the 22q11.2 deletion, a genetic variant strongly associated with psychiatric disease, to test the utility of neuronal Cell Painting in identifying disease relevant phenotypes in a high-throughput setting.** Our work will bring together groups at the Imaging Platform and the Stanley Center to create a new strategy that could be integrated into multiple existing platforms at the Broad to enable, for the first time, the scaled investigation of neuronal profiles. We anticipate that the workflows we will create will facilitate phenotypic screening of neurons at a scale that begins to match the transcriptional revolution, and constitute a key technology to help move from genetics to cellular phenotypes to actionable biology and mechanisms. Gaining insight into neuronal morphology in health and disease will illuminate previously unknown aspects of neuronal biology, enable the interrogation of the effect of the hundreds of genetic risk variants on cellular phenotypes, and greatly complement several existing technologies pioneered at the Broad Institute such as CRISPR screens, drug screens, optical profiling and in situ sequencing to catalyze unprecedented discoveries that link genes and perturbations to neuronal phenotypes.


## Documents

**SPARC Project Proposal:** [(gdoc)](https://docs.google.com/document/d/19uRqfbbwfTVl0vm1ubchO0tccvPs7kpXKlHxpxEDaHU/edit)

**Planning document:** [(gdoc)](https://docs.google.com/document/d/1zEamFSAhJfkR7JPTmALCSpijIo1l7a-KzY32LPFUR48/edit)


## Dataset summary

There are 48 IPSC lines available for this project from the 22q cohort:


|Metadata_line_source |Metadata_line_condition |  n|
|:--------------------|:-----------------------|--:|
|human                |control                 | 22|
|human                |deletion                | 22|
|isogenic_control     |control                 |  2|
|isogenic_deletion    |deletion                |  2|


<details>
  <summary> Code </summary>
  
```r
read_tsv("metadata/NCP_STEM_1/platemap/BR_NCP_STEM_1.txt") %>% 
  distinct(line_ID, line_condition, line_source) %>% count(line_source, line_condition) %>% 
  knitr::kable()
```
  
</details>
