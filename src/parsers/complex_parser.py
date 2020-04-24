import pandas as pd
import argparse

##
## Parsing complexportal file
##

def parse_complex_file(input_file):
    
    # Reading input file as a dataframe:
    df = pd.read_csv(input_file, sep = '\t')
    
    # Parsing relevant fields:
    parsed_table = df.apply(lambda row: {
        'component_id': [x.split('(')[0] for x in row['Identifiers (and stoichiometry) of molecules in complex'].split('|')],
        'complex_id': row['#Complex ac'],
        'complex_name': row['Recommended name'],
        'references': row['Cross references']
    }, axis = 1)

    # Format data into dataframe:
    complex_df = pd.DataFrame(parsed_table.tolist())
    
    # Explode components
    exploded_df = complex_df.explode('component_id').drop_duplicates()

    return exploded_df


if __name__ == '__main__':

    # Parsing commandline arguments
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Complex portal tsv file.')

    parser.add_argument('-i', '--input', help='Input file name.', type=str)
    parser.add_argument('-o', '--output', help='Output file name.', type=str)
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output

    # Open and parse input file:
    complex_table = parse_complex_file(input_file)

    # Save output file:
    complex_table.to_csv(output_file, sep='\t', index=False)


