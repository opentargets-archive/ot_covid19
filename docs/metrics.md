COVID data integration report
================
06 July, 2020

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
| scientificName                               | TARGET INFO                      |   68037 |
| name                                         | TARGET INFO                      |   68008 |
| biotype                                      | TARGET INFO                      |   68008 |
| description                                  | TARGET INFO                      |   65625 |
| uniprot\_ids                                 | TARGET INFO                      |   24132 |
| COVID-19 UniprotKB                           | TARGET INFO                      |      53 |
| FILTER\_network                              | FILTERS                          |    1011 |
| FILTER\_network+drug                         | FILTERS                          |      61 |
| FILTER\_network+covid\_tests                 | FILTERS                          |    1572 |
| Covid\_direct\_interactions                  | PROTEIN INTERACTIONS             |     771 |
| Implicated\_in\_viral\_infection             | PROTEIN INTERACTIONS             |     968 |
| max\_phase                                   | DRUGS FOR TARGET                 |    1183 |
| drugs\_in\_clinic                            | DRUGS FOR TARGET                 |    1183 |
| has\_invitro\_covid\_activity                | DRUGS FOR TARGET                 |     577 |
| invitro\_covid\_activity                     | DRUGS FOR TARGET                 |     577 |
| has\_drug\_in\_covid\_trials                 | DRUGS FOR TARGET                 |     109 |
| hpa\_subcellular\_location                   | BASELINE GENE EXPRESSION         |   12379 |
| hpa\_rna\_tissue\_distribution               | BASELINE GENE EXPRESSION         |   19630 |
| hpa\_rna\_tissue\_specificity                | BASELINE GENE EXPRESSION         |   19630 |
| hpa\_rna\_specific\_tissues                  | BASELINE GENE EXPRESSION         |   11041 |
| respiratory\_system\_is\_expressed           | BASELINE GENE EXPRESSION         |   24507 |
| respiratory\_system\_expressed\_tissue\_list | BASELINE GENE EXPRESSION         |   42368 |
| immune\_system\_is\_expressed                | BASELINE GENE EXPRESSION         |   31320 |
| immune\_system\_expressed\_tissue\_list      | BASELINE GENE EXPRESSION         |   42368 |
| is\_abundance\_reg\_on\_covid                | COVID-19 HOST PROTEIN REGULATION |    1284 |
| abundance\_reg\_on\_covid                    | COVID-19 HOST PROTEIN REGULATION |    1284 |
| Tractability\_Top\_bucket\_(sm)              | TARGET TRACTABILITY              |    5019 |
| Tractability\_Top\_bucket\_(ab)              | TARGET TRACTABILITY              |    9911 |
| Tractability\_Top\_bucket\_(other)           | TARGET TRACTABILITY              |     213 |
| has\_safety\_risk                            | TARGET SAFETY                    |     481 |
| safety\_info\_source                         | TARGET SAFETY                    |     481 |
| safety\_organs\_systems\_affected            | TARGET SAFETY                    |     235 |
| covid\_literature                            | LITERATURE                       |     122 |
