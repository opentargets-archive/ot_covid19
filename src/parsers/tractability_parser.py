import argparse
import pandas as pd
pd.options.mode.chained_assignment = None # Supressing chain copy warnings

# Mapping bucket numbers to description:
# This map was derived from table: https://docs.targetvalidation.org/getting-started/target-tractability
tractability_map = [
    {"ma":"Targets with drugs in phase IV","buckets":1,"sm":"Targets with drugs in phase IV","other":"Targets with drugs in phase IV"},
    {"other":"Targets with drugs in phase II or phase III","sm":"Targets with drugs in phase II or phase III","buckets":2,"ma":"Targets with drugs in phase II or phase III"},
    {"ma":"Targets with drugs in phase 0 or phase I","buckets":3,"sm":"Targets with drugs in phase 0 or phase I","other":"Targets with drugs in phase 0 or phase I"},
    {"sm":"Targets with crystal structures with ligands ","other":None,"ma":"Targets located in the plasma membrane ","buckets":4},
    {"other":None,"sm":"Targets with a drugEBIlity score equal or greater than 0.7","buckets":5,"ma":"Targets with GO cell component terms plasma membrane or secreted"},
    {"ma":"Targets with GO cell component terms plasma membrane or secreted with low or unknown confidence","buckets":6,"sm":"Targets with drugEBIlity between zero and 0.7","other":None},
    {"sm":"Targets with ligands","other":None,"ma":"Targets with predicted signal peptide and transmembrane domains","buckets":7},
    {"ma":"GO cell component - medium confidence","buckets":8,"other":None,"sm":"Targets with a predicted Ro5 druggable domain (druggable genome)"},
    {"ma":"Human Protein Atlas - high confidence","buckets":9,"other":None,"sm":"N.A."}
]
bucket_map = pd.DataFrame(tractability_map)

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

    # Adding top tractability bucket description:
    merged = tractability_df.merge(bucket_map[['sm','buckets']], left_on='Top_bucket_sm', right_on='buckets', how='left')
    merged = merged.merge(bucket_map[['ma','buckets']], left_on='Top_bucket_ab', right_on='buckets', how='left')
    merged = merged.merge(bucket_map[['other','buckets']], left_on='Top_bucket_othercl', right_on='buckets', how='left')

    columns_map = {
        'ensembl_gene_id': 'id',
        'sm': 'Tractability_Top_bucket_(sm)',
        'ma': 'Tractability_Top_bucket_(ab)',
        'other': 'Tractability_Top_bucket_(other)'
    }

    tractability_filterd = merged[list(columns_map.keys())]
    tractability_filterd.rename(columns=columns_map, inplace=True)

    # Saving data:
    tractability_filterd.to_csv(output_parsed_file, sep='\t', index=False)


if __name__ == '__main__':
    main()
