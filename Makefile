# Makefile --- 

# Copyright (C) 2020 Open Targets

# Authors: David Ochoa <ochoa@ebi.ac.uk>

#################################
# Constants
#################################

# Uniprot covid19 flat file
UNIPROTCOVIDQUERY="https://www.ebi.ac.uk/uniprot/api/covid-19/uniprotkb/stream?format=json&query=%2A"
UNIPROTIDMAPPINGURL=ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/HUMAN_9606_idmapping.dat.gz

# OT files
OTTRACTABILITYBUCKET="https://storage.googleapis.com/open-targets-data-releases/21.02/input/annotation-files/tractability_buckets-2021-01-12.tsv"
OTKNOWNTARGETSAFETYBUCKET=https://storage.googleapis.com/open-targets-data-releases/21.02/input/annotation-files/known_target_safety-2021-02-09.json
OTEXPERIMENTALTOXICITYBUCKET=https://storage.googleapis.com/open-targets-data-releases/21.02/input/annotation-files/experimental-toxicity-2020-04-07.tsv
OTBASELINEBUCKET=https://storage.googleapis.com/open-targets-data-releases/21.02/input/annotation-files/baseline_expression_counts-2020-05-07.tsv
OTBASELINETISSUEMAPGITHUB=https://raw.githubusercontent.com/opentargets/expression_hierarchy/master/process/map_with_efos.json
OTEVIDENCEBUCKET=https://storage.googleapis.com/open-targets-data-releases/21.02/output/21.02_evidence_data.json.gz
OTTARGETLISTBUCKET=https://storage.googleapis.com/open-targets-data-releases/21.02/output/21.02_target_list.csv.gz

# Ensembl json
ENSEMBLURL = ftp://ftp.ensembl.org/pub/release-102/json/homo_sapiens/homo_sapiens.json

# COVID complex file:
COVIDCOMPLEXURL=http://ftp.ebi.ac.uk/pub/databases/IntAct/complex/2020-11-05/complextab/sars-cov-2.tsv

# IntAct COVID related interaction query:
INTACTCOVIDURL="https://www.ebi.ac.uk/intact/export?format=mitab_27&query=annot%3A%22dataset%3ACoronavirus%22&negative=false&spoke=false&ontology=false&sort=intact-miscore&asc=false"

# Full human intact data:
INTACTHUMANURL='ftp://ftp.ebi.ac.uk/pub/databases/intact/various/ot_graphdb/2021-01-18/data/interactor_pair_interactions.json'

# HPA
HPAURL=https://www.proteinatlas.org/download/proteinatlas.json.gz

## Wikidata server
WIKIDATASERVER=https://query.wikidata.org/bigdata/namespace/wdq/sparql

#################################
# Paths (Tools)
#################################

# bins
CURL ?= $(shell which curl)
ifeq ($(CURL),)
$(error command "curl" not found)
endif
GUNZIP ?= $(shell which gunzip)
ifeq ($(GUNZIP),)
$(error command "gunzip" not found)
endif
JQ ?= $(shell which jq)
ifeq ($(JQ),)
$(error command "jq" not found)
endif
SED ?= $(shell which sed)
ifeq ($(SED),)
$(error command "sed" not found)
endif
PIPENV ?= $(shell which pipenv)
ifeq ($(PIPENV),)
$(error command "pipenv" not found)
endif
R ?= $(shell which R)
ifeq ($(R),)
$(error command "R" not found)
endif
RSCRIPT ?= $(shell which Rscript)
ifeq ($(RSCRIPT),)
$(error command "Rscript" not found)
endif

#################################
# Paths (DIRECTORIES)
#################################

ROOTDIR := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
SRCDIR= $(ROOTDIR)/src
DATADIR= $(ROOTDIR)/data
TEMPDIR= $(ROOTDIR)/temp
DOCSDIR = $(ROOTDIR)/docs
RAWDIR ?= $(TEMPDIR)/raw_files
PARSEDDIR ?= $(TEMPDIR)/parsed_tables
PREFORMATEDDIR ?= $(TEMPDIR)/preformated_tables
RESULTDIR ?= $(TEMPDIR)/results

REPORT = $(DOCSDIR)/metrics.md
HEADERSFILE = $(DOCSDIR)/headers.csv

#################################
# RAW FILES
#################################

## Uniprot
UNIPROTCOVIDFLATFILE=$(RAWDIR)/uniprot_covid19.json
UNIPROTIDMAPPING=$(RAWDIR)/uniprot_human_idmapping.dat
## Ensembl
ENSEMBL=$(RAWDIR)/ensembl.json
## proteins in human infecting coronavirus
WIKIDATAPROTEINS=$(RAWDIR)/wikidata_proteins.tsv
## OT
OTTRACTABILITY=$(RAWDIR)/ot_tractability.tsv
OTKNOWNTARGETSAFETY=$(RAWDIR)/ot_know_target_safety.json
OTEXPERIMENTALTOXICITY=$(RAWDIR)/ot_experimental_toxicity.tsv
OTBASELINE=$(RAWDIR)/ot_baseline.txt
OTBASELINETISSUEMAP=$(RAWDIR)/ot_map_with_efos.json
OTEVIDENCE=$(RAWDIR)/ot_evidence.json
OTTARGETLIST=$(RAWDIR)/target_list.csv.gz
## Drugs
WIKIDATATRIALS=$(RAWDIR)/wiki_trials.tsv
## Interactions
COVIDCOMPLEX=$(RAWDIR)/complex_sars-cov-2.tsv
INTACTCOVID=$(RAWDIR)/IntAct_SARS-COV-2_interactions.tsv
INTACTHUMAN=$(RAWDIR)/IntAct_homo_sapiens.json
## Baseline/Protein Expression
HPA=$(RAWDIR)/hpa.json
## Protein Abundance in covid
COVIDABUNDACESRAW=$(DATADIR)/bojkova_et_al_nature_covid_abundances.csv
## covid-drugs data (from ChEMBL-Aldo)
DRUGFILE=$(DATADIR)/table_final_drugs_covid.txt
MOA_FILE=$(DATADIR)/dt_pairs_moa_chembl.txt
## MR hits from Mohd 
MR_FILE=$(DATADIR)/gsmr_covid_tool_v2.csv

######################################################
# PARSED FILES - Files with some intermediate parsing
######################################################

## Uniprot - Excalamation mark is added to make sure it is integrated first
UNIPROTCOVIDPARSED=$(PREFORMATEDDIR)/targets/!uniprot_covid19_parsed.tsv
## OT
OTDRUGEVIDENCE=$(PARSEDDIR)/ot_drug_evidence.tsv
OTBASELINEPARSED=$(PREFORMATEDDIR)/targets/ot_baseline_expression_per_anatomical_system.tsv
OTSAFETYPARSED=$(PREFORMATEDDIR)/targets/ot_target_safety.tsv
OTTRACTABILITYPARSED=$(PREFORMATEDDIR)/targets/ot_tractability_parsed.tsv
## Ensembl
ENSEMBLPARSED=$(PARSEDDIR)/ensembl_parsed.json.gz
## UniProt id to Ensembl mapping
UNIPROT2ENSEMBLDRAFT=$(PARSEDDIR)/uniprot2ensembl_draft.tsv
UNIPROT2ENSEMBL=$(PARSEDDIR)/uniprot2ensembl.tsv
## Interactions
COVIDCOMPLEXPARSED=$(PARSEDDIR)/complex_sars-cov-2_parsed.tsv
INTACTCOVIDPARSED=$(PREFORMATEDDIR)/targets/IntAct_SARS-COV-2_interactions_parsed.tsv
## HPA
HPAPREFORMATTED=$(PREFORMATEDDIR)/targets/hpa_parsed.tsv
## Drug info for target
DRUGFORTARGETPARSED=$(PREFORMATEDDIR)/targets/drug_fortarget_parsed.tsv
## Drug info
DRUGSPARSED=$(PARSEDDIR)/drug_info.tsv
## Toy table of drugs in clinical trials for COVID-19
DRUGSCOVID19TRIALSPARSED=$(PREFORMATEDDIR)/drugs/covid19_ct_test.tsv
## complex portal information
COMPLEXPREFORMATTED=$(PREFORMATEDDIR)/targets/complex_portal_preformatted.tsv
## covid-induced protein abundances
COVIDABUNDANCES=$(PREFORMATEDDIR)/targets/covid_abundances.tsv
## covid-related drug data
COVID_TARGET_TRIALS=$(PREFORMATEDDIR)/targets/covid_target_trials.tsv
COVID_TARGET_INVITRO=$(PREFORMATEDDIR)/targets/covid_target_invitro.tsv
## OT literature
OTLITERATUREPARSED=$(PARSEDDIR)/ot_covid_literature_parsed.tsv
OTLITERATUREPREFORMATED=$(PREFORMATEDDIR)/targets/ot_covid_literature.tsv
## MR table:
MRPREFORMATED=$(PREFORMATEDDIR)/targets/mr_hits.tsv


## integrated tables
TARGETSINTEGRATED=$(RESULTDIR)/targets_integrated_data.tsv
DRUGSINTEGRATED=$(RESULTDIR)/drugs_integrated_data.tsv
#############################################################################

#### Phony targets
.PHONY: all setup-environment clean-all clean-parsed clean-results downloads create-temp parsers integrate docs

# ALL
all: setup-environment create-temp downloads parsers integrate docs

clean-all:
	rm -rf $(TEMPDIR)

clean-parsed:
	rm -rf $(TEMPDIR)/parsed_tables
	rm -rf $(TEMPDIR)/preformated_tables
	rm -rf $(TEMPDIR)/results

clean-results:
	rm -f $(TEMPDIR)/results

## Setup environment
setup-environment:
	$(PIPENV) install
	$(R) -q -e 'ifelse(file.exists("renv/library"), renv::restore(), renv::init())'

## Downlad files
downloads: create-temp $(UNIPROTCOVIDFLATFILE) $(UNIPROTIDMAPPING) $(OTTRACTABILITY) $(OTKNOWNTARGETSAFETY) $(OTEXPERIMENTALTOXICITY) \
	$(OTBASELINE) $(OTBASELINETISSUEMAP) $(OTEVIDENCE) $(COVIDCOMPLEX) $(INTACTCOVID) \
	$(WIKIDATATRIALS) $(ENSEMBL) $(HPA) $(INTACTHUMAN) $(OTTARGETLIST)

## TODO: OTDRUGEVIDENCE not yet fully parsed to agreed format.- just a placeholder
parsers: $(OTDRUGEVIDENCE) $(UNIPROTCOVIDPARSED) $(COVIDCOMPLEXPARSED) $(INTACTCOVIDPARSED) \
		$(ENSEMBLPARSED) $(OTBASELINEPARSED) $(HPAPREFORMATTED) $(DRUGFORTARGETPARSED) \
		$(OTTRACTABILITYPARSED) $(OTSAFETYPARSED) $(COMPLEXPREFORMATTED) $(DRUGSPARSED) $(DRUGSCOVID19TRIALSPARSED) \
		$(UNIPROT2ENSEMBL) $(COVIDABUNDANCES) $(COVIDABUNDANCES) $(COVID_TARGET_TRIALS) $(COVID_TARGET_INVITRO) \
		$(OTLITERATUREPREFORMATED) $(MRPREFORMATED)


# CREATES TEMPORARY DIRECTORY
create-temp:
	mkdir -p $(RAWDIR)
	mkdir -p $(PARSEDDIR)
	mkdir -p $(PREFORMATEDDIR)/targets
	mkdir -p $(PREFORMATEDDIR)/drugs
	mkdir -p $(RESULTDIR)

## Run integrator:
integrate: $(TARGETSINTEGRATED) $(DRUGSINTEGRATED)

docs: $(REPORT)

$(REPORT): $(TARGETSINTEGRATED)
	$(RSCRIPT) --no-restore --no-save \
	-e "setwd('$(SRCDIR)')" \
	-e "library(rmarkdown)" \
	-e "HEADERSFILE='$(HEADERSFILE)'" \
	-e "TARGETSINTEGRATED='$(TARGETSINTEGRATED)'" \
	-e "rmarkdown::render('$(SRCDIR)/metrics.Rmd', output_format = 'all', output_file = '$@')"

##
## Fetching data:
##

$(UNIPROTIDMAPPING):
	$(CURL) $(UNIPROTIDMAPPINGURL) | $(GUNZIP) -c > $@

$(UNIPROTCOVIDFLATFILE):
	$(CURL) $(UNIPROTCOVIDQUERY) > $@

$(ENSEMBL):
	$(CURL) $(ENSEMBLURL) | $(JQ) -r '.genes[] | @json' > $(ENSEMBL)

$(WIKIDATAPROTEINS):
	$(CURL) -H "Accept: text/tab-separated-values" -G $(WIKIDATASERVER) --data-urlencode query@$(SRCDIR)/query/virusProteinsAll.rq > $@

$(OTTRACTABILITY):
	$(CURL) $(OTTRACTABILITYBUCKET) > $@

$(OTKNOWNTARGETSAFETY):
	$(CURL) $(OTKNOWNTARGETSAFETYBUCKET) > $@

$(OTEXPERIMENTALTOXICITY):
	$(CURL) $(OTEXPERIMENTALTOXICITYBUCKET) > $@

$(OTBASELINE):
	$(CURL) $(OTBASELINEBUCKET) > $@

$(OTBASELINETISSUEMAP):
	$(CURL) $(OTBASELINETISSUEMAPGITHUB) > $@

$(OTEVIDENCE):
	$(CURL) $(OTEVIDENCEBUCKET) | $(GUNZIP) -c > $@

$(OTTARGETLIST):
	$(CURL) $(OTTARGETLISTBUCKET) > $@	

$(WIKIDATATRIALS):
	$(CURL) -H "Accept: text/tab-separated-values" -G $(WIKIDATASERVER) --data-urlencode query@$(SRCDIR)/query/clinicalTrials.rq > $@

$(COVIDCOMPLEX):
	$(CURL)  $(COVIDCOMPLEXURL) > $@

$(INTACTCOVID):
	$(CURL) $(INTACTCOVIDURL) > $@

$(INTACTHUMAN):
	$(CURL) $(INTACTHUMANURL) > $@	

$(HPA):
	$(CURL) $(HPAURL) | $(GUNZIP) -c | $(JQ) -r '.[] | @json' > $@

##
## Running parser:
##

$(UNIPROTCOVIDPARSED): $(UNIPROTCOVIDFLATFILE)
	$(PIPENV) run python $(SRCDIR)/parsers/uniprot_parser.py -i $(UNIPROTCOVIDFLATFILE) -o $@

$(OTDRUGEVIDENCE):
	$(JQ) -r 'select(.sourceID == "chembl") | [.target.id, .disease.id, .drug.id, .evidence.drug2clinic.clinical_trial_phase.numeric_index, .evidence.target2drug.action_type, .drug.molecule_name] | @tsv' $(OTEVIDENCE) | $(SED) -e 's/http:\/\/identifiers.org\/chembl.compound\///g' > $@

$(OTLITERATUREPARSED):
	$(JQ) -r 'select(.sourceID == "europepmc" and .disease.id == "MONDO_0100096") | [.target.id, .disease.id, .literature.references[].lit_id] | @tsv' $(OTEVIDENCE) > $@

$(OTLITERATUREPREFORMATED): $(OTLITERATUREPARSED)
	$(RSCRIPT) $(SRCDIR)/parsers/literature_get.R $(OTLITERATUREPARSED) $@

$(COVIDCOMPLEXPARSED): $(COVIDCOMPLEX)
	$(PIPENV) run python $(SRCDIR)/parsers/complex_parser.py -i $(COVIDCOMPLEX) -o $(COVIDCOMPLEXPARSED)

$(COMPLEXPREFORMATTED): $(COVIDCOMPLEX) $(COVIDCOMPLEXPARSED)
	$(PIPENV) run python $(SRCDIR)/parsers/complex_portal_parser.py -i $(COVIDCOMPLEXPARSED) -o $(COMPLEXPREFORMATTED)

$(ENSEMBLPARSED) $(UNIPROT2ENSEMBLDRAFT): $(ENSEMBL)
	$(PIPENV) run python $(SRCDIR)/parsers/ensembl_parser.py -i $(ENSEMBL) -o $(ENSEMBLPARSED) -m $(UNIPROT2ENSEMBLDRAFT) -t $(OTTARGETLIST)

$(INTACTCOVIDPARSED): $(INTACTCOVID) $(UNIPROT2ENSEMBL) $(INTACTHUMAN)
	$(PIPENV) run python $(SRCDIR)/parsers/intact_parser.py -i $(INTACTCOVID) -o $@ -m  $(UNIPROT2ENSEMBL) -f $(INTACTHUMAN)

$(OTBASELINEPARSED): $(OTBASELINE) $(OTBASELINETISSUEMAP)
	$(PIPENV) run python $(SRCDIR)/parsers/baseline_parser.py -i $(OTBASELINE) -m $(OTBASELINETISSUEMAP) -o $@

$(HPAPREFORMATTED): $(HPA)
	$(PIPENV) run python $(SRCDIR)/parsers/hpa_parser.py -i $(HPA) -o $@

$(DRUGFORTARGETPARSED): $(OTDRUGEVIDENCE)
	$(PIPENV) run python $(SRCDIR)/parsers/target_druginfo_parser.py -i $(OTDRUGEVIDENCE) -o $@ -e target

$(OTTRACTABILITYPARSED): $(OTTRACTABILITY)
	$(PIPENV) run python $(SRCDIR)/parsers/tractability_parser.py -i $(OTTRACTABILITY) -o $@

$(OTSAFETYPARSED): $(OTKNOWNTARGETSAFETY) $(OTEXPERIMENTALTOXICITY) $(ENSEMBLPARSED)
	$(PIPENV) run python $(SRCDIR)/parsers/safety_parser.py -k $(OTKNOWNTARGETSAFETY) -e $(OTEXPERIMENTALTOXICITY) -g $(ENSEMBLPARSED) -o $(OTSAFETYPARSED) -a

$(DRUGSPARSED): $(OTDRUGEVIDENCE)
	$(PIPENV) run python $(SRCDIR)/parsers/target_druginfo_parser.py -i $(OTDRUGEVIDENCE) -o $@ -e drug

$(DRUGSCOVID19TRIALSPARSED): $(OTDRUGEVIDENCE)
	$(PIPENV) run python $(SRCDIR)/parsers/target_druginfo_parser.py -i $(OTDRUGEVIDENCE) -o $@ -e covid19_trials

$(UNIPROT2ENSEMBL): $(ENSEMBLPARSED) $(UNIPROTIDMAPPING)
	$(PIPENV) run python $(SRCDIR)/parsers/Ensembl-Uniprot_map_generator.py -u $(UNIPROTIDMAPPING) -e $(UNIPROT2ENSEMBLDRAFT) -o $@

$(COVIDABUNDANCES): $(UNIPROT2ENSEMBL)
	$(RSCRIPT) $(SRCDIR)/parsers/abundances_get.R $(COVIDABUNDACESRAW) $(UNIPROT2ENSEMBL) $@ 2>&1 >/dev/null

$(MRPREFORMATED): $(ENSEMBLPARSED) $(MR_FILE)
	$(PIPENV) run python $(SRCDIR)/parsers/mr_parser.py -i $(MR_FILE) -o $@ -e $(ENSEMBLPARSED)

$(COVID_TARGET_TRIALS) $(COVID_TARGET_INVITRO): $(UNIPROT2ENSEMBL)
	$(RSCRIPT) $(SRCDIR)/parsers/covid_trials.R \
	$(UNIPROT2ENSEMBL) \
	$(DRUGFILE) \
	$(MOA_FILE) \
	$(COVID_TARGET_TRIALS) \
	$(COVID_TARGET_INVITRO) 2>&1 >/dev/null



##
## Integrate files:
##
##Files with target info
$(TARGETSINTEGRATED): parsers
		$(PIPENV) run python $(SRCDIR)/integrators/covid_data_integration.py \
			-r $(ENSEMBLPARSED) \
			-o $(TARGETSINTEGRATED) \
			-i $(PREFORMATEDDIR)/targets \
			-c $(SRCDIR)/integrators/integration_config.json \
			-e targets

##Files with drug info
$(DRUGSINTEGRATED): parsers
		$(PIPENV) run python $(SRCDIR)/integrators/covid_data_integration.py \
			-r $(DRUGSPARSED) \
			-o $(DRUGSINTEGRATED) \
			-i $(PREFORMATEDDIR)/drugs \
			-c $(SRCDIR)/integrators/integration_config.json \
			-e drugs
