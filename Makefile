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

#### Phony targets
.PHONY: all downloads create-temp

# ALL
all: create-temp downloads

#############
# Downloads
#############

downloads: create-temp $(UNIPROTCOVIDFLATFILE) $(OTTRACTABILITY) $(OTSAFETY) $(OTBASELINE) $(OTEVIDENCE)

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
