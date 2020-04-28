import json
import argparse

def get_tissue_mappings(mapping_filename):
    """Return a dictionary that maps tissue names to anatomical systems and organs"""

    with open(mapping_filename, 'r') as mappings_file:
        mapping_dict = json.load(mappings_file)
        return mapping_dict['tissues']


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


if __name__ == '__main__':
    main()
