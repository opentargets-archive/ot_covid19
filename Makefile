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

# COVID complex file:
COVIDCOMPLEXURL=http://ftp.ebi.ac.uk/pub/databases/IntAct/complex/current/complextab/sars-cov-2.tsv

# IntAct COVID related interaction query:
INTACTCOVIDURL="https://www.ebi.ac.uk/intact/export?format=mitab_27&query=annot%3A%22dataset%3ACoronavirus%22&negative=false&spoke=false&ontology=false&sort=intact-miscore&asc=false" 

#################################
# Paths (DIRECTORIES)
#################################

ROOTDIR := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
TEMPDIR= $(ROOTDIR)/temp
SRCDIR= $(ROOTDIR)/src
DATADIR= $(ROOTDIR)/temp

#################################
# Paths (Tools)
#################################

# bins
CURL ?= $(shell which curl)
GUNZIP ?= $(shell which gunzip)

#################################
# Relevant files
#################################

UNIPROTCOVIDFLATFILE=$(TEMPDIR)/uniprot_covid19.dat
OTTRACTABILITY=$(TEMPDIR)/ot_tractability.tsv
OTSAFETY=$(TEMPDIR)/ot_safety.json
OTBASELINE=$(TEMPDIR)/ot_baseline.txt
OTEVIDENCE=$(TEMPDIR)/ot_evidence.json
COVIDCOMPLEX=$(TEMPDIR)/complex_sars-cov-2.tsv  
INTACTCOVID=$(TEMPDIR)/IntAct_SARS-COV-2_interactions.tsv

#### Phony targets
.PHONY: all downloads create-temp

# ALL
all: create-temp downloads

#############
# Downloads
#############

downloads: create-temp $(UNIPROTCOVIDFLATFILE) $(OTTRACTABILITY) $(OTSAFETY) $(OTBASELINE) $(OTEVIDENCE) $(COVIDCOMPLEX) $(INTACTCOVID)

# CREATES TEMPORARY DIRECTORY
create-temp:
	mkdir -p $(TEMPDIR)

$(UNIPROTCOVIDFLATFILE):
	$(CURL) $(UNIPROTCOVIDFTP) > $@

$(OTTRACTABILITY):
	$(CURL) $(OTTRACTABILITYBUCKET) > $@

$(OTSAFETY):
	$(CURL) $(OTSAFETYBUCKET) > $@

$(OTBASELINE):
	$(CURL) $(OTBASELINEBUCKET) > $@

$(OTEVIDENCE):
	$(CURL) $(OTEVIDENCEBUCKET) | $(GUNZIP) -c > $@

$(COVIDCOMPLEX):
	$(CURL)  $(COVIDCOMPLEXURL) > $@

$(INTACTCOVID):
	$(CURL) $(INTACTCOVIDURL) > $@


