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
        
        
    def add_data(self, data_df, parameters):
        """
        Adding new data to the integrator
        """
        ##
        ## Checking merge parameters
        ##
        
        # Checking columns of intereset:
        columns = parameters['columns'] if 'columns' in parameters else []
        
        # Check flag:
        flag = parameters['flag'] if 'flag' in parameters else False
        
        # Flag label must be set if flag is true:
        if flag:  
            try:
                flag_label = parameters['flag_label']
                columns.append(flag_label)
            except ValueError as e:
                raise e('If adding flag is required, the column name has to be set (flag_label key)!')
                
        # How to join:
        how = parameters['how'] if 'how' in parameters else 'left'
        
        # Is there any columns to map to existing columns?
        columns_to_map = parameters['columns_to_map'] if 'columns_to_map' in parameters else {}  
        
        ##
        ## Updating data
        ##
        
        # Adding flag to the dataframe:
        if flag:
            data_df[flag_label] = True

        # Renaming columns to avoid confusion:
        protected_columns = columns.append('id')
        column_rename_map = {x : x+'_temp' for x in data_df.columns if x not in columns}
        data_df.rename(columns=column_rename_map, inplace=True)

        ##
        ## Join data:
        ##
        
        merged = self.ensembl_df.merge(data_df, how=how, on='id')
        self.merged = merged
        ##
        ## Cleaning merged data:
        ##
        
        # Removing temporary columns:
        merged.drop(list(column_rename_map.values()), axis=1, inplace=True)
        
        # Adding false values to flag column:
        if flag:
            merged[flag_label].loc[merged[flag_label]!=True] = False
            
        # Update dataframe:
        self.ensembl_df = merged
        
    def get_integrated_data(self):
        return self.ensembl_df
    
    
    def save_integrated(self, file_name='test.tsv'):
        if '.tsv' in file_name:
            self.ensembl_df.to_csv(file_name, sep='\t', index=False)
        if '.xlsx' in file_name:
            self.ensembl_df.to_excel(file_name, index=False)




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
        data_df = pd.read_csv('{}/{}'.format(input_folder, source_file), sep='\t')
        integrator.add_data(data_df, parameters=parameters)


if __name__ == '__main__':
    main()