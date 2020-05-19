# COVID19 Open Targets data integration

## Aim
Centralise publicly available datasets in order to build a Virus – Host Target Knowledgebase for Drug Target Selection. 

A full description of the project vision is [here](https://drive.google.com/open?id=1NzbSrh_Cqs9yCIyl-J7HjCHfNFtkVNdQ)
Some of the questions the project is trying to answer [here](https://docs.google.com/document/d/1Tcc0lhu5YqT3-fY5N4EzPjYtd-dcKhM5y-Lu1TqGD30/edit#heading=h.clav1w5t1yv0)

## Contributors
This project is open to contributors.

## Data flow

1. Potential data sources are fetched based on URLs provided in the `Makefile` if such URL is not available, the data tables can be directly added to the `/data` folder.
2. Relevant pieces of information is extracted from the raw source data as part of a parsing step.
3. Data might be further processed if necessary eg. mapping cross-references, integration with other sources etc.
4. Pre-processed tables are then picked up by the integrator script(s) and compiled into presentable tables.

## Data sources
The pipeline integrates information about human and viral targets from the following sources:

|Name|Source|Description|
| :--- | ------|-----------|
| Human gene information | Ensembl | Information about human genes |
| COVID-19 UniProtKB| UniProt | UniProt site with information about SARS and SARS-CoV-2 proteins  |
| SARS-CoV-2 Complexes | IntAct | Information about SARS-CoV-2 protein complexes |
| Human - virus interactome| IntAct | Human - SARS-CoV-2 interactome from [Gordon et al. 2020](https://www.nature.com/articles/s41586-020-2286-9) plus intercations of human proteins with proteins of other viruses based on IntAct data |
| Human interactome| IntAct | Human protein-protein interactions from IntAct database |
| Baseline expression per anatomical systems | Open Targets | Baseline gene expression per anatomical systems provided by Expression Atlas group used in the Open Targets Platform |
| Baseline expression distribution and specificity | Human protein Atlas | Information about subcellular location of proteins, tissue distribution and tissue specificity as provided by HPA |
| Protein expression during SARS-CoV-2 infection| Bojkova et al. 2020 | Information about proteins whose abundance is regulated during viral infection from [Bojkova et al. 2020](https://www.nature.com/articles/s41586-020-2332-7) paper |
| Target Tractability| Open Targets | [Target tractability assessment for small molecules, antibodies and other modalities provided by ChEMBL and used in the Open Targets Platform](https://docs.targetvalidation.org/getting-started/target-tractability) |
| Target Safety | Open Targets| [Manually curated target safety data used in the Open Targets Platform](https://docs.targetvalidation.org/getting-started/target-safety)   |
| Target Drugs | Open Targets | [Information about drugs extracted from the ChEMBL evidence file used in the Open Targets platform](https://docs.targetvalidation.org/data-sources/drugs) |
| Drugs in COVID-19 clinical trials| ChEMBL| Drugs in clinical trials against COVID-19 |
| Active compounds in COVID-19 in vitro assays| ChEMBL | Compounds shown to be active in COVID-19 in vitro assays provided by ChEMBL|

Other files not listed in the table are also used for supporting purposes such as gene id mappings.

## Usage

#### Prerequisites
The following programs have to be installed and available in order to run the pipeline:
* Python 3.7
* [Pipenv](https://github.com/pypa/pipenv): Recommended v2018.11.26 or newer. If using a package manager check the version installed, since version v11.9.0 available in Ubuntu does not work.
* [jq](https://stedolan.github.io/jq/) 
* [R](https://www.r-project.org/) 4.0.0

The pipeline has been run successfully with those dependencies on macOS (Catalina) and Ubuntu (20.04 LTS).

#### Run project from scratch

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

#### Integration configuration

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

