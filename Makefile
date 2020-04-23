# Makefile --- 

# Copyright (C) 2020 Open Targets

# Authors: David Ochoa <ochoa@ebi.ac.uk>

#################################
# Constants
#################################

# Uniprot covid19 flat file
UNIPROTCOVIDFTP=ftp://ftp.uniprot.org/pub/databases/uniprot/pre_release/covid-19.dat
# OT files
OTTRACTABILITYBUCKET=https://storage.googleapis.com/open-targets-data-releases/20.04/input/annotation-files/tractability_buckets-2020-03-26.tsv
OTSAFETYBUCKET=https://storage.googleapis.com/open-targets-data-releases/20.04/input/annotation-files/known_target_safety-2020-04-01.json
OTBASELINEBUCKET=https://github.com/opentargets/expression_analysis/blob/master/exp_summary_NormCounts_genes.txt
OTEVIDENCEBUCKET=https://storage.googleapis.com/open-targets-data-releases/20.04/output/20.04_evidence_data.json.gz

# Ensembl json
ENSEMBLURL = ftp://ftp.ensembl.org/pub/release-99/json/homo_sapiens/homo_sapiens.json

# COVID complex file:
COVIDCOMPLEXURL=http://ftp.ebi.ac.uk/pub/databases/IntAct/complex/current/complextab/sars-cov-2.tsv

# IntAct COVID related interaction query:
INTACTCOVIDURL="https://www.ebi.ac.uk/intact/export?format=mitab_27&query=annot%3A%22dataset%3ACoronavirus%22&negative=false&spoke=false&ontology=false&sort=intact-miscore&asc=false"

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
TEMPDIR= $(ROOTDIR)/temp
SRCDIR= $(ROOTDIR)/src
DATADIR= $(ROOTDIR)/temp

#################################
# Relevant files
#################################

## Uniprot
UNIPROTCOVIDFLATFILE=$(TEMPDIR)/uniprot_covid19.dat
UNIPROTCOVIDPARSED=$(TEMPDIR)/uniprot_covid19_parsed.tsv
## Ensembl
ENSEMBL=$(TEMPDIR)/ensembl.json
## proteins in human infecting coronavirus
WIKIDATAPROTEINS=$(TEMPDIR)/wikidata_proteins.tsv
## OT
OTTRACTABILITY=$(TEMPDIR)/ot_tractability.tsv
OTSAFETY=$(TEMPDIR)/ot_safety.json
OTBASELINE=$(TEMPDIR)/ot_baseline.txt
OTEVIDENCE=$(TEMPDIR)/ot_evidence.json
## Drugs
OTDRUGEVIDENCE=$(TEMPDIR)/ot_drug_evidence.tsv
WIKIDATATRIALS=$(TEMPDIR)/wiki_trials.tsv
CHEMBLMOLECULE=$(TEMPDIR)/chembl_molecules.json
CHEMBLDRUGINDICATION=$(TEMPDIR)/chembl_indication.json
CHEMBLTARGETS=$(TEMPDIR)/chembl_targets.json
CHEMBLTARGETCOMPONENTS=$(TEMPDIR)/chembl_target_components.json
CHEMBLMOA=$(TEMPDIR)/chembl_mechanisms.json

## Interactions
COVIDCOMPLEX=$(TEMPDIR)/complex_sars-cov-2.tsv
INTACTCOVID=$(TEMPDIR)/IntAct_SARS-COV-2_interactions.tsv

#### Phony targets
.PHONY: all downloads create-temp parsers

# ALL
all: create-temp downloads parsers

#############
# Downloads
#############

downloads: create-temp $(UNIPROTCOVIDFLATFILE) $(OTTRACTABILITY) $(OTSAFETY) $(OTBASELINE) $(OTEVIDENCE) $(COVIDCOMPLEX) $(INTACTCOVID) $(WIKIDATATRIALS) $(CHEMBLMOLECULE) $(CHEMBLDRUGINDICATION) $(CHEMBLTARGETCOMPONENTS) $(CHEMBLTARGETS) $(CHEMBLMOA) $(ENSEMBL)

## TODO: OTDRUGEVIDENCE not yet fully parsed to agreed format.- just a placeholder
parsers: $(OTDRUGEVIDENCE) $(UNIPROTCOVIDPARSED)

# CREATES TEMPORARY DIRECTORY
create-temp:
	mkdir -p $(TEMPDIR)

$(UNIPROTCOVIDFLATFILE):
	$(CURL) $(UNIPROTCOVIDFTP) > $@

$(UNIPROTCOVIDPARSED): $(UNIPROTCOVIDFLATFILE)
	$(PIPENV) run python $(SRCDIR)/parsers/uniprot_parser.py -i $(UNIPROTCOVIDFLATFILE) > $@

$(ENSEMBL):
	$(CURL) $(ENSEMBLURL) | $(JQ) -r '.genes[] | @json' > $(ENSEMBL)

$(WIKIDATAPROTEINS):
	$(CURL) -H "Accept: text/tab-separated-values" -G $(WIKIDATASERVER) --data-urlencode query@$(SRCDIR)/query/virusProteinsAll.rq > $@

$(OTTRACTABILITY):
	$(CURL) $(OTTRACTABILITYBUCKET) > $@

$(OTSAFETY):
	$(CURL) $(OTSAFETYBUCKET) > $@

$(OTBASELINE):
	$(CURL) $(OTBASELINEBUCKET) > $@

$(OTEVIDENCE):
	$(CURL) $(OTEVIDENCEBUCKET) | $(GUNZIP) -c > $@

$(OTDRUGEVIDENCE):
	$(JQ) -r 'select(.sourceID == "chembl") | [.target.id, .disease.id, .drug.id, .evidence.drug2clinic.clinical_trial_phase.numeric_index, .evidence.target2drug.action_type, .drug.molecule_name] | @tsv' $(OTEVIDENCE) | $(SED) -e 's/http:\/\/identifiers.org\/chembl.compound\///g' > $@

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

