# COVID19 Open Targets data integration

## Aim
Centralise publicly available datasets in order to build a Virus – Host Target Knowledgebase for Drug Target Selection. 

A full description of the project vision is [here](https://drive.google.com/open?id=1NzbSrh_Cqs9yCIyl-J7HjCHfNFtkVNdQ)
Some of the questions the project is trying to answer [here](https://docs.google.com/document/d/1Tcc0lhu5YqT3-fY5N4EzPjYtd-dcKhM5y-Lu1TqGD30/edit#heading=h.clav1w5t1yv0)

## Data flow

1. Potential data sources are fetched based on URLs provided in the `Makefile` if such URL is not available, the data tables can be directly added to the `/data` folder.
2. Relevant pieces of information is extracted from the raw source data as part of a parsing step.
3. Data might be further processed if necessary eg. mapping cross-references, integration with other sources etc.
4. Pre-processed tables are then picked up by the integrator script(s) and compiled into presentable tables.

## Usage

#### Run project from scratch:

```bash
git clone https://github.com/opentargets/ot_covid19
cd ot_covid19
make all
```

`make all` downloads all data, builds Python environment, run parsers and the integrator script(s).

#### Other actions:

* `make setup-environment` - building Python environment
* `make downloads` - download files only
* `make parsers` - run parsers only
* `make integrator` - run integrator(s) only
* `make clean-all` - removing temporary files.

## Directory structure

**Data folders**:

* `/data` - containing version controlled data files that cannot be directly accessed from the web
* `/temp` - created by `make` will be populated when run locally. Data under this folder is not versioned
* `/temp/raw_files` - raw data files fetched from the web
* `/temp/parsed_tables` - parsed tables
* `/temp/preformated_tables` - pre-processed data ready to be integrated

**Script folders**:

* `/src/parsers` - contains parser scripts
* `/src/query` - contains SQL queries
* `/src/integrators` - contains integrator scripts

## Data integration

For the integration part the concept is that we want to keep out logic altogether from the integrator scripts. All data processing steps should happen earlier in the parsing and pre-processing steps. Integrator scripts take tables with columns that are ready to be added to the final tables. So there are a few requirements:

1. Tables are read from `/temp/preformated_tables` directory only
2. The tables must be in an uncompressed tsv format
2. Tables must have a column called `id` containing unique identifiers (eg. Ensembl gene id or Uniprot primary accession)
3. Tables to be integrated must be added to the integration config files describing how the integration should happen

#### Integration configuration:

This recipe shows how to integrate a dataset were we are expecting new targets (eg viral proteins) that are not included in the complete human gene set:

```json
"uniprot_covid19_parsed.tsv": {
    "columns": [], 
    "flag": true, 
    "flag_label": "COVID-19 UniprotKB", 
    "how": "outer", 
    "columns_to_map": {
        "taxon_id": "taxon_id",
        "uniprot_ids": "uniprot_accessions"
    }
}
```
Where:

* `columns` contains the list of columns to be added. It can be empty if only flag is used.
* `flag` - boolean, indicating if the table is used as a flag eg. marking genes that are in the COVID-19 uniprot dataset
* `flag_label` - title of the flag column
* `how` - describing how the join should happen. By default it is left. Use outer if you expect new targets in the integrated dataset
* `columns_to_map` - column mapping to populate existing fields for the new targets.


This recipe shows how to integrate a dataset where we are not expecting new targets, and two new columns are added to the final table:

```json
"ot_drugs_processed.tsv": {
    "columns": ["drug_names", "max_phase"], 
    "flag": false
}
```

