import json
import argparse

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


if __name__ == '__main__':
    main()
