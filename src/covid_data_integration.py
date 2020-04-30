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

    # 2. Integrate the following files. For each files indicate which columns to be joined. If left empty, just a flag will be added. 
    input_to_parse = {
        'uniprot_covid19_parsed.tsv': {
            'columns': [], # columns to add.
            'flag': True, # Generate just a flag (indicating if a given gene/protein) is in the integrated dataset
            'label': 'COVID-19 UniprotKB', # Label of the flag column.
            'how': 'outer', # How to merge the tables
            'columns_to_map': {
                'taxon_id': 'taxon_id',
                'uniprot_ids': 'uniprot_accessions'
            }
        }
    }

    # Integrating all parsed datasets:
    for source_file, parameters in input_to_parse.items():
        integrator.add_data(source_file, parameters=parameters)



if __name__ == '__main__':
    main()