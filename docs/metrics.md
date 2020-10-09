COVID data integration report
================
09 October, 2020

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

    ## Warning: Unknown levels in `f`: ensembl_id, drugs_in_covid_trials

| variable                                     | Category                         | targets |
| :------------------------------------------- | :------------------------------- | ------: |
| scientificName                               | TARGET INFO                      |   27639 |
| name                                         | TARGET INFO                      |   27610 |
| biotype                                      | TARGET INFO                      |   27610 |
| description                                  | TARGET INFO                      |   27418 |
| uniprot\_ids                                 | TARGET INFO                      |   19872 |
| COVID-19 UniprotKB                           | TARGET INFO                      |      57 |
| FILTER\_network                              | FILTERS                          |    7639 |
| FILTER\_network+drug                         | FILTERS                          |     395 |
| FILTER\_network+covid\_tests                 | FILTERS                          |    7961 |
| Covid\_direct\_interactions                  | PROTEIN INTERACTIONS             |    1653 |
| Covid\_indirect\_interactions                | PROTEIN INTERACTIONS             |    6781 |
| Implicated\_in\_viral\_infection             | PROTEIN INTERACTIONS             |    1904 |
| max\_phase                                   | DRUGS FOR TARGET                 |    1191 |
| drugs\_in\_clinic                            | DRUGS FOR TARGET                 |    1191 |
| has\_invitro\_covid\_activity                | DRUGS FOR TARGET                 |     522 |
| invitro\_covid\_activity                     | DRUGS FOR TARGET                 |     522 |
| has\_drug\_in\_covid\_trials                 | DRUGS FOR TARGET                 |      99 |
| hpa\_subcellular\_location                   | BASELINE GENE EXPRESSION         |   12297 |
| hpa\_rna\_tissue\_distribution               | BASELINE GENE EXPRESSION         |   19347 |
| hpa\_rna\_tissue\_specificity                | BASELINE GENE EXPRESSION         |   19347 |
| hpa\_rna\_specific\_tissues                  | BASELINE GENE EXPRESSION         |   10838 |
| respiratory\_system\_is\_expressed           | BASELINE GENE EXPRESSION         |   20124 |
| respiratory\_system\_expressed\_tissue\_list | BASELINE GENE EXPRESSION         |   26021 |
| immune\_system\_is\_expressed                | BASELINE GENE EXPRESSION         |   22765 |
| immune\_system\_expressed\_tissue\_list      | BASELINE GENE EXPRESSION         |   26021 |
| is\_abundance\_reg\_on\_covid                | COVID-19 HOST PROTEIN REGULATION |    1147 |
| abundance\_reg\_on\_covid                    | COVID-19 HOST PROTEIN REGULATION |    1147 |
| Tractability\_Top\_bucket\_(sm)              | TARGET TRACTABILITY              |    5035 |
| Tractability\_Top\_bucket\_(ab)              | TARGET TRACTABILITY              |    9882 |
| Tractability\_Top\_bucket\_(other)           | TARGET TRACTABILITY              |     215 |
| has\_safety\_risk                            | TARGET SAFETY                    |     439 |
| safety\_info\_source                         | TARGET SAFETY                    |     439 |
| safety\_organs\_systems\_affected            | TARGET SAFETY                    |     193 |
| covid\_literature                            | LITERATURE                       |     264 |
