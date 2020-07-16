COVID data integration report
================
16 July, 2020

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
| scientificName                               | TARGET INFO                      |   27625 |
| name                                         | TARGET INFO                      |   27596 |
| biotype                                      | TARGET INFO                      |   27596 |
| description                                  | TARGET INFO                      |   27406 |
| uniprot\_ids                                 | TARGET INFO                      |   19896 |
| COVID-19 UniprotKB                           | TARGET INFO                      |      38 |
| FILTER\_network                              | FILTERS                          |    4760 |
| FILTER\_network+drug                         | FILTERS                          |     220 |
| FILTER\_network+covid\_tests                 | FILTERS                          |    5188 |
| Covid\_direct\_interactions                  | PROTEIN INTERACTIONS             |     678 |
| Covid\_indirect\_interactions                | PROTEIN INTERACTIONS             |    4304 |
| Implicated\_in\_viral\_infection             | PROTEIN INTERACTIONS             |     850 |
| max\_phase                                   | DRUGS FOR TARGET                 |    1183 |
| drugs\_in\_clinic                            | DRUGS FOR TARGET                 |    1183 |
| has\_invitro\_covid\_activity                | DRUGS FOR TARGET                 |     522 |
| invitro\_covid\_activity                     | DRUGS FOR TARGET                 |     522 |
| has\_drug\_in\_covid\_trials                 | DRUGS FOR TARGET                 |      99 |
| hpa\_subcellular\_location                   | BASELINE GENE EXPRESSION         |   12301 |
| hpa\_rna\_tissue\_distribution               | BASELINE GENE EXPRESSION         |   19359 |
| hpa\_rna\_tissue\_specificity                | BASELINE GENE EXPRESSION         |   19359 |
| hpa\_rna\_specific\_tissues                  | BASELINE GENE EXPRESSION         |   10844 |
| respiratory\_system\_is\_expressed           | BASELINE GENE EXPRESSION         |   20039 |
| respiratory\_system\_expressed\_tissue\_list | BASELINE GENE EXPRESSION         |   26492 |
| immune\_system\_is\_expressed                | BASELINE GENE EXPRESSION         |   23450 |
| immune\_system\_expressed\_tissue\_list      | BASELINE GENE EXPRESSION         |   26492 |
| is\_abundance\_reg\_on\_covid                | COVID-19 HOST PROTEIN REGULATION |    1149 |
| abundance\_reg\_on\_covid                    | COVID-19 HOST PROTEIN REGULATION |    1149 |
| Tractability\_Top\_bucket\_(sm)              | TARGET TRACTABILITY              |    4976 |
| Tractability\_Top\_bucket\_(ab)              | TARGET TRACTABILITY              |    8867 |
| Tractability\_Top\_bucket\_(other)           | TARGET TRACTABILITY              |     184 |
| has\_safety\_risk                            | TARGET SAFETY                    |     439 |
| safety\_info\_source                         | TARGET SAFETY                    |     439 |
| safety\_organs\_systems\_affected            | TARGET SAFETY                    |     193 |
| covid\_literature                            | LITERATURE                       |     122 |
