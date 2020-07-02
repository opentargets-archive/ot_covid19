COVID data integration report
================
02 July, 2020

# Data available

``` r
df %>%
    gather("variable", "value", -ensembl_id) %>%
    filter(!is.na(value)) %>%
    filter(value != "") %>%
    filter(value != FALSE) %>%
    inner_join(descriptors %>% select(Category, Header), by = c("variable" = "Header")) %>%
    group_by(variable, Category) %>%
    summarise(targets = n()) %>%
    ungroup() %>%
    mutate(variable = fct_relevel(variable, descriptors$Header)) %>%
    arrange(variable) %>%
    knitr::kable()
```

    ## Warning: Unknown levels in `f`: ensembl_id, Covid_indirect_interactions,
    ## drugs_in_covid_trials

| variable                                     | Category                         | targets |
| :------------------------------------------- | :------------------------------- | ------: |
| scientificName                               | TARGET INFO                      |   68027 |
| name                                         | TARGET INFO                      |   67998 |
| biotype                                      | TARGET INFO                      |   67998 |
| description                                  | TARGET INFO                      |   65599 |
| uniprot\_ids                                 | TARGET INFO                      |   24139 |
| COVID-19 UniprotKB                           | TARGET INFO                      |      38 |
| FILTER\_network                              | FILTERS                          |    1001 |
| FILTER\_network+drug                         | FILTERS                          |      56 |
| FILTER\_network+covid\_tests                 | FILTERS                          |    1540 |
| Covid\_direct\_interactions                  | PROTEIN INTERACTIONS             |     771 |
| Implicated\_in\_viral\_infection             | PROTEIN INTERACTIONS             |     968 |
| max\_phase                                   | DRUGS FOR TARGET                 |    1174 |
| drugs\_in\_clinic                            | DRUGS FOR TARGET                 |    1174 |
| has\_invitro\_covid\_activity                | DRUGS FOR TARGET                 |     541 |
| invitro\_covid\_activity                     | DRUGS FOR TARGET                 |     541 |
| has\_drug\_in\_covid\_trials                 | DRUGS FOR TARGET                 |     109 |
| hpa\_subcellular\_location                   | BASELINE GENE EXPRESSION         |   12382 |
| hpa\_rna\_tissue\_distribution               | BASELINE GENE EXPRESSION         |   19635 |
| hpa\_rna\_tissue\_specificity                | BASELINE GENE EXPRESSION         |   19635 |
| hpa\_rna\_specific\_tissues                  | BASELINE GENE EXPRESSION         |   11044 |
| respiratory\_system\_is\_expressed           | BASELINE GENE EXPRESSION         |   24254 |
| respiratory\_system\_expressed\_tissue\_list | BASELINE GENE EXPRESSION         |   48339 |
| immune\_system\_is\_expressed                | BASELINE GENE EXPRESSION         |   34047 |
| immune\_system\_expressed\_tissue\_list      | BASELINE GENE EXPRESSION         |   48339 |
| is\_abundance\_reg\_on\_covid                | COVID-19 HOST PROTEIN REGULATION |    1294 |
| abundance\_reg\_on\_covid                    | COVID-19 HOST PROTEIN REGULATION |    1294 |
| Tractability\_Top\_bucket\_(sm)              | TARGET TRACTABILITY              |    4981 |
| Tractability\_Top\_bucket\_(ab)              | TARGET TRACTABILITY              |    8961 |
| Tractability\_Top\_bucket\_(other)           | TARGET TRACTABILITY              |     184 |
| has\_safety\_risk                            | TARGET SAFETY                    |     481 |
| safety\_info\_source                         | TARGET SAFETY                    |     481 |
| safety\_organs\_systems\_affected            | TARGET SAFETY                    |     235 |
