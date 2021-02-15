COVID data integration report
================
15 February, 2021

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
|:---------------------------------------------|:---------------------------------|--------:|
| scientificName                               | TARGET INFO                      |   27682 |
| name                                         | TARGET INFO                      |   27650 |
| biotype                                      | TARGET INFO                      |   27650 |
| description                                  | TARGET INFO                      |   27628 |
| uniprot\_ids                                 | TARGET INFO                      |   19882 |
| COVID-19 UniprotKB                           | TARGET INFO                      |      92 |
| FILTER\_network                              | FILTERS                          |    8573 |
| FILTER\_network+drug                         | FILTERS                          |     439 |
| FILTER\_network+covid\_tests                 | FILTERS                          |    8874 |
| Covid\_direct\_interactions                  | PROTEIN INTERACTIONS             |    2009 |
| Covid\_indirect\_interactions                | PROTEIN INTERACTIONS             |    7566 |
| Implicated\_in\_viral\_infection             | PROTEIN INTERACTIONS             |    2387 |
| max\_phase                                   | DRUGS FOR TARGET                 |    1202 |
| drugs\_in\_clinic                            | DRUGS FOR TARGET                 |    1202 |
| has\_invitro\_covid\_activity                | DRUGS FOR TARGET                 |     520 |
| invitro\_covid\_activity                     | DRUGS FOR TARGET                 |     520 |
| has\_drug\_in\_covid\_trials                 | DRUGS FOR TARGET                 |      99 |
| hpa\_subcellular\_location                   | BASELINE GENE EXPRESSION         |   12709 |
| hpa\_rna\_tissue\_distribution               | BASELINE GENE EXPRESSION         |   19364 |
| hpa\_rna\_tissue\_specificity                | BASELINE GENE EXPRESSION         |   19364 |
| hpa\_rna\_specific\_tissues                  | BASELINE GENE EXPRESSION         |   10848 |
| respiratory\_system\_is\_expressed           | BASELINE GENE EXPRESSION         |   20132 |
| respiratory\_system\_expressed\_tissue\_list | BASELINE GENE EXPRESSION         |   26039 |
| immune\_system\_is\_expressed                | BASELINE GENE EXPRESSION         |   22778 |
| immune\_system\_expressed\_tissue\_list      | BASELINE GENE EXPRESSION         |   26039 |
| is\_abundance\_reg\_on\_covid                | COVID-19 HOST PROTEIN REGULATION |    1145 |
| abundance\_reg\_on\_covid                    | COVID-19 HOST PROTEIN REGULATION |    1145 |
| Tractability\_Top\_bucket\_(sm)              | TARGET TRACTABILITY              |    5030 |
| Tractability\_Top\_bucket\_(ab)              | TARGET TRACTABILITY              |    9890 |
| Tractability\_Top\_bucket\_(other)           | TARGET TRACTABILITY              |     222 |
| has\_safety\_risk                            | TARGET SAFETY                    |     439 |
| safety\_info\_source                         | TARGET SAFETY                    |     439 |
| safety\_organs\_systems\_affected            | TARGET SAFETY                    |     193 |
| covid\_literature                            | LITERATURE                       |    1096 |
