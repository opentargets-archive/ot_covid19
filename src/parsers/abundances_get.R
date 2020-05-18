suppressPackageStartupMessages(library(tidyverse))

args <- commandArgs(trailingOnly = TRUE)
inputFile <- args[1]
mappingsFile <- args[2]
outputFile <- args[3]

pvalue_cutoff <- 0.01 ## Constant


map <- read_tsv(mappingsFile, col_types = cols())
df <- read_csv(file = inputFile, comment = "", col_types = cols())

## reading, renaming, grouping, summarise
out <- df %>%
    rename(acc = `UniProt Accession`) %>%
    select(acc, contains("Ratio"), contains("P value")) %>%
    gather("column", "value", -acc) %>%
    mutate(column = str_replace_all(column, "P value", "P-value")) %>%
    separate(column, c("variable", "time"), " ") %>%
    spread(variable, value) %>%
    mutate(ratio_string = ifelse(Ratio > 0, "up", "down")) %>%
    mutate(ratio_simple = paste(time,"(",ratio_string,")", sep = "")) %>%
    group_by(acc) %>%
    summarise(is_abundance_reg_on_covid = any(`P-value` < pvalue_cutoff),
              abundance_reg_on_covid = paste(ratio_simple[`P-value` < pvalue_cutoff], collapse = ";")) %>%
    mutate(acc = strsplit(acc, ";")) %>%
    unnest() %>%
    inner_join(map, by = c("acc" = "uniprot_id")) %>%
    select(-acc) %>%
    rename(id = ensembl_id) %>%
    distinct() %>%
    mutate(abundance_reg_on_covid = str_split(abundance_reg_on_covid, ";")) %>%
    group_by(id) %>%
    summarise(is_abundance_reg_on_covid = any(is_abundance_reg_on_covid),
              abundance_reg_on_covid = paste(unique(unlist(abundance_reg_on_covid)), collapse = ";"))

## printing output
out %>%
    write_tsv(outputFile)
