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
        
        ensembl_data = []

        # loading ensembl file (compressed json):
        with gzip.open(ensemblFile,'rt') as f:
            for line in f:
                gene_row = json.loads(line)
                ensembl_data.append(gene_row)
        
        print('[Info] Readind data complete. Number of genes: {}'.format(len(ensembl_data)))
        print('[Info] Processing data...')
        
        # Once data is read, we fomat into a data frame:
        ensembl_df = pd.DataFrame(ensembl_data)
        
        # Merging arrays:
        ensembl_df.drop(columns=['PDB'], inplace=True)
        ensembl_df.MIM_morbidity = ensembl_df.MIM_morbidity.apply(lambda x: ','.join([y['display_id'] for y in x]) if len(x)>0 else None)
        ensembl_df.uniprot_ids = ensembl_df.uniprot_ids.apply(lambda x: ','.join(x) if len(x) > 0 else None)
        
        self.ensembl_df = ensembl_df


    def add_data(self, data, columns=[], flag=False):
        """
        Adding a new set of data. 
        """





def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='This script integrates COVID-19 related datasets into a single table.')

    parser.add_argument('-r', '--reference', help='File with the reference dataset.', required=True, type=str)
    parser.add_argument('-c', '--config', help='Configuration file describing integration recipes.', required=True, type=str)
    parser.add_argument('-i', '--inputFolder', help='Folder from which the integrated files are read.', required=True, type=str)
    parser.add_argument('-o', '--output', help='Output file name.', required=True, type=str)

    args = parser.parse_args()

    # Get parameters:
    config_file = args.config
    ensembl_file = args.reference
    input_folder = args.inputFolder
    output_file = args.output

    ## TODO: add tests here.

    # 1. Generate first table.
    covid_core_data = integrator(ensemblFile)

    # 2. Reading configuration:
    with open(config_file, 'rt') as f:
        config_data = json.load(f)

    # Integrating all parsed datasets:
    for source_file, parameters in config_data.items():
        integrator.add_data('{}/{}'.format(input_folder, source_file), parameters=parameters)


if __name__ == '__main__':
    main()