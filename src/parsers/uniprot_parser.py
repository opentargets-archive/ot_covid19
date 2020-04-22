#!/usr/bin/env python3

import os
import sys
import argparse
import Bio.SwissProt as sp

###########
# MAIN
###########

if __name__ == '__main__':
  # Reading arguments
  parser = argparse \
    .ArgumentParser(
      description='Parse uniprot .dat file')
  parser.add_argument('-i',
                      '--inputfile',
                      required=True,
                      action="store",
                      metavar="PATH",
                      dest="UNIPROT_IN",
                      help='input uniprot dat file to parse')
  # parser.add_argument('-o',
  #                     '--outputfile',
  #                     required=True,
  #                     action="store",
  #                     metavar="PATH",
  #                     dest="UNIPROT_OUT",
  #                     help='path for parsed uniprot file')

  results = parser.parse_args()
  UNIPROTFILE = results.UNIPROT_IN
  # OUTPUTFILE = results.UNIPROT_OUT

  ## TODO: parse appropiately
  ## For future reference on fields
  ## https://biopython.org/DIST/docs/api/Bio.SwissProt-pysrc.html
  with open(UNIPROTFILE) as handle:
    records = sp.parse(handle)
    for record in records:
      print(record.entry_name)
      print(",".join(record.accessions))
      print(repr(record.organism))
      print("\n")
