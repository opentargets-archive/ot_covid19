import pandas as pd 
import argparse
import gzip
import json

# 

"""
This script integrates all COVID-19 related datasets into a single table
"""

class DataIntegrator(object):

    def __init__(self, ensemblFile):

        # Openind and parsing ensembl file (compressed json):
        with 





def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='This script integrates COVID-19 related datasets into a single table.')

    # parser.add_argument('-i', '--input', help='Folder with the input file.', required=True, type=str)
    parser.add_argument('-e', '--ensemblFile', help='The Ensembl input file.', required=True, type=str)
    # parser.add_argument('-o', '--output', help='Output file name.', required=True, type=str)

    args = parser.parse_args()

    # Get parameters:
    # inputFolder = args.input
    # output = args.output
    ensemblFile = args.ensemblFile

    # 1. Generate first table.
    covid_core_data = integrator(ensemblFile)

    # 2. Integrate 



if __name__ == '__main__':
    main()