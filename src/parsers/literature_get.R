suppressPackageStartupMessages(library(tidyverse))

args <- commandArgs(trailingOnly = TRUE)
inputFile <- args[1]
outputFile <- args[2]


df <- read_tsv(file = inputFile, comment = "", col_types = cols()) %>%
    setNames(c("id", "disease", "literature")) %>%
    ## black-list SARS1 target
    filter(id != "ENSG00000031698")


## reading, renaming, grouping, summarise
out <- df %>%
    group_by(id) %>%
    summarise(covid_literature = n_distinct(literature))

## printing output
out %>%
    write_tsv(outputFile)
