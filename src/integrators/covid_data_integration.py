import pandas as pd 
import argparse
import gzip
import json
import requests
from os import listdir
from os.path import isfile, join

# 

"""
This script integrates all COVID-19 related datasets into a single table
"""

def fetch_organism(tax_ids=[]):
    base_url = 'https://www.ebi.ac.uk/ena/data/taxonomy/v1/taxon/tax-id/'
    return_data = []

    for tax_id in tax_ids:
        try:
            return_data.append(requests.get(base_url+str(tax_id)).json())
        except Exception as e:
            print(e)
            print('[Error] Failed to fetch organism data.')

    # Get all unique species:
    try:
        df = pd.DataFrame(return_data)
        df.taxId = df.taxId.astype(float)
        return df
    except:
        return None


class TargetDataIntegrator(object):

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

        # Mapping values from the new data:
        for col1, col2 in columns_to_map.items():
            merged[col1] = merged[col1].fillna(merged[col2+"_temp"])
        
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


    def map_taxonomy(self):

        # Get a unique set of taxonomy identifiers:
        tax_ids = [int(x) for x in self.ensembl_df.taxon_id.unique() if x == x ]

        if len(tax_ids) == 0:
            return

        # Map IDs to taxonomy object:
        tax_df= fetch_organism(tax_ids)

        # Merging data wih taxonomy df:
        merged = self.ensembl_df.merge(tax_df[['scientificName','taxId']], left_on='taxon_id', right_on='taxId', how='left')
        merged.drop(['taxon_id','taxId'], axis=1, inplace=True)

        # Update:
        self.ensembl_df = merged

    def add_filter_columns(self):
        integrated_df = self.ensembl_df

        ##
        ## Filter No1: Any of the networks OR uniprot implicated.
        ##
        integrated_df['FILTER_network'] =  (
            integrated_df['COVID-19 UniprotKB'] | 
            (~ integrated_df['COVID_complex_names'].isna()) | 
            (~ integrated_df['Covid_direct_interactions'].isna()) | 
            (~ integrated_df['Covid_indirect_interactions'].isna()) | 
            (integrated_df['Implicated_in_viral_infection'] == True)
        )


        ##
        ## Filter No2: Any networks AND Phase3 or 4 trial
        ##
        integrated_df['FILTER_network+drug'] = (
            integrated_df['FILTER_network'] &
            integrated_df['max_phase'] > 2
        )

        # Update dataframe:
        self.ensembl_df = integrated_df


class DrugDataIntegrator(object):

    def __init__(self, drugFile):

        self.drug_df = pd.read_csv(drugFile, sep='\t', header=0)

        print('[Info] Reading data complete. Number of drugs: {}'.format(len(self.drug_df.index)))
        print('[Info] Processing data...')

    def add_data(self, data_df, parameters):
        """
        Adding new drug data to the integrator
        """
        ##
        ## Checking merge parameters
        ##

        # Checking columns of intereset:
        columns = parameters['columns'] if 'columns' in parameters else []

        # How to join:
        how = parameters['how'] if 'how' in parameters else 'left'

        ##
        ## Join data:
        ##

        merged = self.drug_df.merge(data_df, how=how, on='id')
        self.drug_df = merged

    def get_integrated_data(self):
        return self.drug_df

    def save_integrated(self, file_name='test.tsv'):
        if '.tsv' in file_name:
            self.drug_df.to_csv(file_name, sep='\t', index=False)
        if '.xlsx' in file_name:
            self.drug_df.to_excel(file_name, index=False)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='This script integrates COVID-19 related datasets into a single table.')

    parser.add_argument('-r', '--reference', help='File with the reference dataset.', required=True, type=str)
    parser.add_argument('-c', '--config', help='Configuration file describing integration recipes.', required=True, type=str)
    parser.add_argument('-i', '--inputFolder', help='Folder from which the integrated files are read.', required=True, type=str)
    parser.add_argument('-o', '--output', help='Output file name.', required=True, type=str)
    parser.add_argument('-e', '--entity', help='Type of the entity contained in the tables to be merged.', required=True,
                        choices=['targets', 'drugs'])

    args = parser.parse_args()

    # Get parameters:
    config_file = args.config
    reference_file = args.reference
    input_folder = args.inputFolder
    output_file = args.output
    entity_type = args.entity

    # Reading files from the preformatted folder:
    preformatted_files = [f for f in listdir(input_folder) if isfile(join(input_folder, f))]
    print('[Info] Integrating the following files:\n\t{}'.format('\n\t'.join(preformatted_files)))

    # 1. Generate first table.
    if entity_type == "targets":
        integrator_obj = TargetDataIntegrator(reference_file)
    else:
        integrator_obj = DrugDataIntegrator(reference_file)

    # 2. Reading configuration:
    with open(config_file, 'rt') as f:
        config_data = json.load(f)

    # Integrating all parsed datasets:
    for preformatted_file in preformatted_files:

        # try open file:
        try:
            data_df = pd.read_csv('{}/{}'.format(input_folder, preformatted_file), sep='\t')
        except:
            print('[Error] Could not open {} as tsv.'.format(preformatted_file))
            raise

        # Testing if table has id:
        if 'id' not in data_df.columns.tolist():
            raise ValueError('The table must have \'id\' column to join.')

        # Read or generate join parameters:
        parameters = config_data[preformatted_file] if preformatted_file in config_data else {'columns':data_df.columns.tolist()}

        # Integrating:
        integrator_obj.add_data(data_df, parameters)

    # Map taxonomy to species and apply filters:
    if entity_type == "targets":
        integrator_obj.map_taxonomy()
        integrator_obj.add_filter_columns()

    # Save data:
    integrator_obj.save_integrated(output_file)


if __name__ == '__main__':
    main()
