import json
import pandas as pd
import argparse
import logging
import copy

logger = logging.getLogger(__name__)

def get_tissue_mappings(mapping_filename):
    """Return a dictionary that maps tissue names to anatomical systems and organs"""

    with open(mapping_filename, 'r') as mappings_file:
        mapping_dict = json.load(mappings_file)
        return mapping_dict['tissues']

def initialise_expression_dict(mapping_dictionary):

    # Extract anatomical systems
    anatomical_systems = set()
    for tissues, mappings in mapping_dictionary.items():
        anatomical_systems.update(mappings['anatomical_systems'])

    # Initialise scoring dictionary
    expression_dict={}
    for anatomical_system in anatomical_systems:
        # Remove white spaces
        anatomical_system_clean_name = anatomical_system.strip().replace(" ", "_")
        expression_dict[anatomical_system_clean_name] = {
            'is_expressed' : False,
            'expressed_tissue_list' : []
        }

    return expression_dict

def parse_baseline(baseline_filename, tissue_mapping, output_filename):


    baseline_df = pd.read_csv(baseline_filename, sep='\t', header=0, index_col=0)

    # Check that column names in baseline file exist in mapping file
    columns_to_drop = []
    for column in baseline_df.columns:
        if column not in tissue_mapping:
            logger.warning("{} is not a supported tissue, skipping it".format(column))
            columns_to_drop.append(column)

    # Drop unmapped tissues
    if columns_to_drop:
        baseline_df.drop(columns_to_drop, axis=1, inplace=True)

    empty_expression_dict = initialise_expression_dict(tissue_mapping)
    expression_per_anatomical_systems_list = []
    # Iterate all genes
    for gene, expression in baseline_df.to_dict('index').items():
        expression_per_anatomical_systems_dict = copy.deepcopy(empty_expression_dict)
        expression_per_anatomical_systems_dict['id'] = gene
        for tissue in expression:
            # Gene is considered expressed if > 6 tpm
            if expression[tissue] > 6:
                for anat_sys in tissue_mapping[tissue]['anatomical_systems']:
                    # Remove white spaces
                    anat_sys_clean_name = anat_sys.strip().replace(" ", "_")
                    expression_per_anatomical_systems_dict[anat_sys_clean_name]['is_expressed'] = True
                    expression_per_anatomical_systems_dict[anat_sys_clean_name]['expressed_tissue_list'].append(tissue)
        expression_per_anatomical_systems_list.append(expression_per_anatomical_systems_dict)
    expression_per_anatomical_systems_df = pd.json_normalize(expression_per_anatomical_systems_list, max_level=1, sep="_")

    # Drop anatomical systems where no gene is expressed - happens for sensory system
    # Find columns with single unique value - only "is_expressed" columns can be used as lists are not hashable
    columns_count_unique = expression_per_anatomical_systems_df.filter(regex="is_expressed").nunique()
    columns_single_unique_value = columns_count_unique[columns_count_unique==1].index

    # Check that the unique values are either False or empty list
    empty_columns = []
    for column in columns_single_unique_value:
        unique_value = expression_per_anatomical_systems_df[column].unique()[0]
        if unique_value == False:
            # Add both "is_expressed" column and list column to list to be removed
            empty_columns.append(column)
            empty_columns.append(column.replace("is_expressed", "expressed_tissue_list"))
    expression_per_anatomical_systems_df.drop(columns=empty_columns, inplace=True)

    # Write to file
    expression_per_anatomical_systems_df.to_csv(output_filename, sep='\t', index=False)

def main():

    # Parse CLI parameters
    parser = argparse.ArgumentParser(description='Parse baseline expression file and report the anatomical systems where each target is expressed.')
    parser.add_argument('-i','--input',
                        help='Baseline expression tab-separated file',
                        type=str, default='ot_baseline.tsv')

    parser.add_argument('-m','--mapping',
                        help='Name of file that maps tissues to anatomical systems',
                        type=str, default='ot_map_with_efos.json')

    parser.add_argument('-o','--output',
                        help='Output file name',
                        type=str, default='baseline_expression_per_anatomical_system.tsv')



    args = parser.parse_args()

    # Get parameters:
    input_file = args.input
    mapping_file = args.mapping
    output_file = args.output

    # Load tissue mappings
    tissue_mappings = get_tissue_mappings(mapping_file)
    parse_baseline(input_file, tissue_mappings, output_file)

if __name__ == '__main__':
    main()
