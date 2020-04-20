# Makefile --- 

# Copyright (C) 2020 Open Targets

# Authors: David Ochoa <ochoa@ebi.ac.uk>

#################################
# Constants
#################################

# Uniprot covid19 flat file
UNIPROTCOVIDFTP=ftp://ftp.uniprot.org/pub/databases/uniprot/pre_release/covid-19.dat

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


#################################
# Relevant files
#################################

# Files
UNIPROTCOVIDFLATFILE=$(TEMPDIR)/uniprot_covid19.dat


#### Phony targets
.PHONY: all R-deps test

# ALL
all: create-temp $(UNIPROTCOVIDFLATFILE)

# CREATES TEMPORARY DIRECTORY
create-temp:
	mkdir -p $(TEMPDIR)

$(UNIPROTCOVIDFLATFILE): create-temp
	$(CURL) $(UNIPROTCOVIDFTP) > $@
