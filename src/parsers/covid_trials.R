suppressPackageStartupMessages(library(tidyverse))

args <- commandArgs(trailingOnly = TRUE)
mappingsFile <- args[1]
drugFile <- args[2]
actives_moa_File <- args[3]
covid_trials_output <- args[4]
covid_invitro_output <- args[5]

# read files
map <- read_tsv(mappingsFile, col_types = cols())
drug <- read_tsv(drugFile, col_types = cols())
actives_moa <- read_tsv(actives_moa_File, col_types = cols())

## covid clinical trials
covid_trials <- drug %>%
    select(molecule_chembl_id, IN_TRIALS, PREF_NAME) %>%
    filter(IN_TRIALS == 1) %>%
    inner_join(actives_moa %>%
               select(molecule_chembl_id, uniprot_id),
               by = c("molecule_chembl_id")) %>%
    inner_join(map, by = c("uniprot_id" = "uniprot_id")) %>%
    select(-uniprot_id, -molecule_chembl_id) %>%
    rename(id = ensembl_id, has_drug_in_covid_trials = IN_TRIALS) %>%
    mutate(has_drug_in_covid_trials = as.logical(has_drug_in_covid_trials)) %>%
    distinct() %>%
    group_by(id, has_drug_in_covid_trials) %>%
    summarise(drugs_in_covid_trials = paste(PREF_NAME, collapse = ";")) %>%
    ungroup()

covid_trials %>%
    write_tsv(covid_trials_output)


## covid19 preclinical studies
## drug %>%
##     select(molecule_chembl_id, PRECLINICAL, PREF_NAME) %>%
##     filter(PRECLINICAL == 1) %>%
##     inner_join(actives_moa %>%
##                select(molecule_chembl_id, uniprot_id),
##                by = c("molecule_chembl_id")) %>%
##     inner_join(map, by = c("uniprot_id" = "uniprot_id")) %>%
##     select(-uniprot_id, -molecule_chembl_id) %>%
##     rename(id = ensembl_id, has_drug_in_covid_preclinical = PRECLINICAL) %>%
##     distinct() %>%
##     group_by(id, has_drug_in_covid_preclinical) %>%
##     summarise(drugs_in_covid_preclinical = paste(PREF_NAME, collapse = ";"))


## covid19 invitro assays
legend <- list("-1" = "not tested",
               "0" = "inactive",
               "0.2" = "weakly active and cytotoxic",
               "0.3" = "highly active and cytotoxic",
               "0.5" = "weakly active",
               "1" = "highly active")

covid_invitro <- drug %>%
    select(molecule_chembl_id, PREF_NAME, contains("ACTIVE")) %>%
    gather("assay", "value", -molecule_chembl_id, -PREF_NAME) %>%
    filter(value != -1) %>%
    mutate(assay = str_replace_all(assay, "_ACTIVE", "")) %>%
    mutate(has_invitro_covid_activity = value > 0) %>%
    mutate(value = unlist(legend[as.character(value)])) %>%
    mutate(newlabel = paste(PREF_NAME, value, paste("(",assay,")", sep = ""))) %>%
    select(molecule_chembl_id, has_invitro_covid_activity, newlabel) %>%
    distinct() %>%
    inner_join(actives_moa %>%
               select(molecule_chembl_id, uniprot_id),
               by = c("molecule_chembl_id")) %>%
    inner_join(map, by = c("uniprot_id" = "uniprot_id")) %>%
    select(-uniprot_id, -molecule_chembl_id) %>%
    rename(id = ensembl_id) %>%
    distinct() %>%
    group_by(id) %>%
    summarise(invitro_covid_activity = paste(newlabel, collapse = ";"),
              has_invitro_covid_activity = paste(sum(has_invitro_covid_activity),n(), sep = "/"))

covid_invitro %>%
    write_tsv(covid_invitro_output)

