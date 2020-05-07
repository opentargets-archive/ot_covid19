# Makefile --- 

# Copyright (C) 2020 Open Targets

# Authors: David Ochoa <ochoa@ebi.ac.uk>

#################################
# Constants
#################################

# Uniprot covid19 flat file
UNIPROTCOVIDQUERY="https://www.ebi.ac.uk/uniprot/api/covid-19/uniprotkb/download?format=json&query=%2A"
UNIPROTIDMAPPINGURL=ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/HUMAN_9606_idmapping.dat.gz

# OT files
OTTRACTABILITYBUCKET=https://storage.googleapis.com/open-targets-data-releases/20.04/input/annotation-files/tractability_buckets-2020-03-26.tsv
OTKNOWNTARGETSAFETYBUCKET=https://storage.googleapis.com/open-targets-data-releases/20.04/input/annotation-files/known_target_safety-2020-04-01.json
OTEXPERIMENTALTOXICITYBUCKET=https://storage.googleapis.com/open-targets-data-releases/20.04/input/annotation-files/experimental-toxicity-2020-04-07.tsv
OTBASELINEBUCKET=https://storage.googleapis.com/open-targets-data-releases/20.04/input/annotation-files/exp_summary_NormCounts_genes_all_Blueprint2_v2-2020-04-01.txt
OTBASELINETISSUEMAPGITHUB=https://raw.githubusercontent.com/opentargets/expression_hierarchy/master/process/map_with_efos.json
OTEVIDENCEBUCKET=https://storage.googleapis.com/open-targets-data-releases/20.04/output/20.04_evidence_data.json.gz

# Ensembl json
ENSEMBLURL = ftp://ftp.ensembl.org/pub/release-99/json/homo_sapiens/homo_sapiens.json

# COVID complex file:
COVIDCOMPLEXURL=http://ftp.ebi.ac.uk/pub/databases/IntAct/complex/current/complextab/sars-cov-2.tsv

# IntAct COVID related interaction query:
INTACTCOVIDURL="https://www.ebi.ac.uk/intact/export?format=mitab_27&query=annot%3A%22dataset%3ACoronavirus%22&negative=false&spoke=false&ontology=false&sort=intact-miscore&asc=false"

# HPA
HPAURL=https://www.proteinatlas.org/download/proteinatlas.json.gz

# Drug ChEMBL
CHEMBLMOLECULEURL=https://www.ebi.ac.uk/chembl/api/data/molecule.json
CHEMBLDRUGINDICATIONURL=https://www.ebi.ac.uk/chembl/api/data/drug_indication.json
CHEMBLTARGETSURL=https://www.ebi.ac.uk/chembl/api/data/target.json
CHEMBLTARGETCOMPONENTSURL=https://www.ebi.ac.uk/chembl/api/data/target_component.json
CHEMBLMOAURL=https://www.ebi.ac.uk/chembl/api/data/mechanism.json

## Wikidata server
WIKIDATASERVER=https://query.wikidata.org/bigdata/namespace/wdq/sparql

#################################
# Paths (Tools)
#################################

# bins
CURL ?= $(shell which curl)
GUNZIP ?= $(shell which gunzip)
JQ ?= $(shell which jq)
SED ?= $(shell which sed)
PIPENV ?= $(shell which pipenv)

#################################
# Paths (DIRECTORIES)
#################################

ROOTDIR := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
SRCDIR= $(ROOTDIR)/src
DATADIR= $(ROOTDIR)/data
TEMPDIR= $(ROOTDIR)/temp
RAWDIR ?= $(TEMPDIR)/raw_files
PARSEDDIR ?= $(TEMPDIR)/parsed_tables
PREFORMATEDDIR ?= $(TEMPDIR)/preformated_tables
RESULTDIR ?= $(TEMPDIR)/results

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
## Drugs
WIKIDATATRIALS=$(RAWDIR)/wiki_trials.tsv
CHEMBLMOLECULE=$(RAWDIR)/chembl_molecules.json
CHEMBLDRUGINDICATION=$(RAWDIR)/chembl_indication.json
CHEMBLTARGETS=$(RAWDIR)/chembl_targets.json
CHEMBLTARGETCOMPONENTS=$(RAWDIR)/chembl_target_components.json
CHEMBLMOA=$(RAWDIR)/chembl_mechanisms.json
## Interactions
COVIDCOMPLEX=$(RAWDIR)/complex_sars-cov-2.tsv
INTACTCOVID=$(RAWDIR)/IntAct_SARS-COV-2_interactions.tsv
## Baseline/Protein Expression
HPA=$(RAWDIR)/hpa.json

######################################################
# PARSED FILES - Files with some intermediate parsing
######################################################

## Uniprot
UNIPROTCOVIDPARSED=$(PREFORMATEDDIR)/targets/uniprot_covid19_parsed.tsv
## OT
OTDRUGEVIDENCE=$(PARSEDDIR)/ot_drug_evidence.tsv
OTBASELINEPARSED=$(PREFORMATEDDIR)/targets/ot_baseline_expression_per_anatomical_system.tsv
OTSAFETYPARSED=$(PREFORMATEDDIR)/targets/ot_target_safety.tsv
OTTRACTABILITYPARSED=$(PREFORMATEDDIR)/targets/ot_tractability_parsed.tsv
## Ensembl
ENSEMBLPARSED=$(PARSEDDIR)/ensembl_parsed.json.gz
## Interactions
COVIDCOMPLEXPARSED=$(PARSEDDIR)/complex_sars-cov-2_parsed.tsv
INTACTCOVIDPARSED=$(PARSEDDIR)/IntAct_SARS-COV-2_interactions_parsed.tsv
## HPA
HPAPREFORMATTED=$(PREFORMATEDDIR)/targets/hpa_parsed.tsv
## Drug info for target
DRUGFORTARGETPARSED=$(PREFORMATEDDIR)/targets/drug_fortarget_parsed.tsv
## Drug info
DRUGSPARSED=$(PARSEDDIR)/drug_info.tsv
## Toy table of drugs in clinical trials for COVID-19
DRUGSCOVID19TRIALSPARSED=$(PREFORMATEDDIR)/drugs/covid19_ct_test.tsv

###############################################################
# PREFORMATED FILES - Files already formatted to be integrated
###############################################################

COMPLEXPREFORMATTED=$(PREFORMATEDDIR)/targets/complex_portal_preformatted.tsv
TARGETSINTEGRATED=$(RESULTDIR)/targets_integrated_data.tsv
DRUGSINTEGRATED=$(RESULTDIR)/drugs_integrated_data.tsv

#############################################################################

#### Phony targets
.PHONY: all setup-environment clean-all downloads create-temp parsers integrate

# ALL
all: setup-environment create-temp downloads parsers integrate

clean-all:
	rm -rf $(TEMPDIR)

## Setup environment
setup-environment:
	$(PIPENV) install

## Downlad files
downloads: create-temp $(UNIPROTCOVIDFLATFILE) $(UNIPROTIDMAPPING) $(OTTRACTABILITY) $(OTKNOWNTARGETSAFETY) $(OTEXPERIMENTALTOXICITY) \
	$(OTBASELINE) $(OTBASELINETISSUEMAP) $(OTEVIDENCE) $(COVIDCOMPLEX) $(INTACTCOVID) \
	$(WIKIDATATRIALS) $(CHEMBLMOLECULE) $(CHEMBLDRUGINDICATION) $(CHEMBLTARGETCOMPONENTS) \
	$(CHEMBLTARGETS) $(CHEMBLMOA) $(ENSEMBL) $(HPA)

## TODO: OTDRUGEVIDENCE not yet fully parsed to agreed format.- just a placeholder
parsers: $(OTDRUGEVIDENCE) $(UNIPROTCOVIDPARSED) $(COVIDCOMPLEXPARSED) $(INTACTCOVIDPARSED) \
		$(ENSEMBLPARSED) $(OTBASELINEPARSED) $(HPAPREFORMATTED) $(DRUGFORTARGETPARSED) \
		$(OTTRACTABILITYPARSED) $(OTSAFETYPARSED) $(COMPLEXPREFORMATTED) $(DRUGSPARSED) $(DRUGSCOVID19TRIALSPARSED)

# CREATES TEMPORARY DIRECTORY
create-temp:
	mkdir -p $(TEMPDIR)
	mkdir -p $(RAWDIR)
	mkdir -p $(PARSEDDIR)
	mkdir -p $(PREFORMATEDDIR)/targets
	mkdir -p $(PREFORMATEDDIR)/drugs
	mkdir -p $(RESULTDIR)

## Run integrator:
integrate: $(INTEGRATED)

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

$(CHEMBLMOLECULE):
	$(CURL) $(CHEMBLMOLECULEURL) > $@

$(CHEMBLDRUGINDICATION):
	$(CURL) $(CHEMBLDRUGINDICATIONURL) > $@

$(CHEMBLTARGETCOMPONENTS):
	$(CURL) $(CHEMBLTARGETCOMPONENTSURL) > $@

$(CHEMBLTARGETS):
	$(CURL) $(CHEMBLTARGETSURL) > $@

$(CHEMBLMOA):
	$(CURL) $(CHEMBLMOAURL) > $@

$(WIKIDATATRIALS):
	$(CURL) -H "Accept: text/tab-separated-values" -G $(WIKIDATASERVER) --data-urlencode query@$(SRCDIR)/query/clinicalTrials.rq > $@

$(COVIDCOMPLEX):
	$(CURL)  $(COVIDCOMPLEXURL) > $@

$(INTACTCOVID):
	$(CURL) $(INTACTCOVIDURL) > $@

$(HPA):
	$(CURL) $(HPAURL) | $(GUNZIP) -c | $(JQ) -r '.[] | @json' > $@

##
## Running parser:
##

$(UNIPROTCOVIDPARSED): $(UNIPROTCOVIDFLATFILE)
	$(PIPENV) run python $(SRCDIR)/parsers/uniprot_parser.py -i $(UNIPROTCOVIDFLATFILE) -o $@

$(OTDRUGEVIDENCE):
	$(JQ) -r 'select(.sourceID == "chembl") | [.target.id, .disease.id, .drug.id, .evidence.drug2clinic.clinical_trial_phase.numeric_index, .evidence.target2drug.action_type, .drug.molecule_name] | @tsv' $(OTEVIDENCE) | $(SED) -e 's/http:\/\/identifiers.org\/chembl.compound\///g' > $@

$(COVIDCOMPLEXPARSED): $(COVIDCOMPLEX)
	$(PIPENV) run python $(SRCDIR)/parsers/complex_parser.py -i $(COVIDCOMPLEX) -o $(COVIDCOMPLEXPARSED)

$(COMPLEXPREFORMATTED): $(COVIDCOMPLEX) $(COVIDCOMPLEXPARSED)
	$(PIPENV) run python $(SRCDIR)/parsers/complex_portal_parser.py -i $(COVIDCOMPLEXPARSED) -o $(COMPLEXPREFORMATTED)

$(ENSEMBLPARSED): $(COVIDCOMPLEX)
	$(PIPENV) run python $(SRCDIR)/parsers/ensembl_parser.py -i $(ENSEMBL) -o $(ENSEMBLPARSED)

$(INTACTCOVIDPARSED): $(INTACTCOVID)
	$(PIPENV) run python $(SRCDIR)/parsers/intact_parser.py -i $(INTACTCOVID) -o $(INTACTCOVIDPARSED)

$(OTBASELINEPARSED): $(OTBASELINE) $(OTBASELINETISSUEMAP)
	$(PIPENV) run python $(SRCDIR)/parsers/baseline_parser.py -i $(OTBASELINE) -m $(OTBASELINETISSUEMAP) -o $(OTBASELINEPARSED)

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

##
## Integrate files:
##
##Files with target info
$(INTEGRATED): parsers
		$(PIPENV) run python $(SRCDIR)/integrators/covid_data_integration.py \
			-r $(ENSEMBLPARSED) \
			-o $(TARGETSINTEGRATED) \
			-i $(PREFORMATEDDIR)/targets \
			-c $(SRCDIR)/integrators/integration_config.json
			-e targets

##Files with drug info
$(INTEGRATED): parsers
		$(PIPENV) run python $(SRCDIR)/integrators/covid_data_integration.py \
			-r $(DRUGSPARSED) \
			-o $(DRUGSINTEGRATED) \
			-i $(PREFORMATEDDIR)/drugs \
			-c $(SRCDIR)/integrators/integration_config.json
			-e drugs