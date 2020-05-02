import argparse
import pandas as pd
pd.options.mode.chained_assignment = None # Supressing chain copy warnings

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='This script parses tractability data.')

    parser.add_argument('-i', '--input', help='OT tractability tsv file.', required=True, type=str)
    parser.add_argument('-o', '--output', help='Output tsv file of the parsed tractability file.', required=True, type=str)

    args = parser.parse_args()
    input_tractability_file = args.input
    output_parsed_file = args.output 

    tractability_df = pd.read_csv(input_tractability_file, sep='\t')

    # This is the list of columns we are extracting from the tractability data and how they are called in the new data:
    columns_map = {
        'ensembl_gene_id': 'id',
        'DrugEBIlity_score': 'DrugEBIlity_score',
        'Small_Molecule_Druggable_Genome_Member': 'In druggable genome',
        'Top_bucket_sm': 'Tractability Top bucket (sm)',
        'Top_bucket_ab': 'Tractability Top bucket (ab)',
        'Top_bucket_othercl': 'Tractability Top bucket (other)'
    }

    # Filtering tractability data:
    tractability_filterd = tractability_df[list(columns_map.keys())]
    tractability_filterd.rename(columns=columns_map, inplace=True)

    # Update flag to boolean:
    tractability_filterd['In druggable genome'] = tractability_filterd['In druggable genome'].apply(lambda x: True if x == 'Y' else False)

    # SAving data:
    tractability_filterd.to_csv(output_parsed_file, sep='\t', index=False)


if __name__ == '__main__':
    main()
