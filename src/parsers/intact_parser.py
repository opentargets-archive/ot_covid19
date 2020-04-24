import pandas as pd
import argparse
import re

# Parse interactor type:
def parse_interactor_type(x):
    pattern = '\((.+)\)'
    try:
        return re.search(pattern,x).group(1)
    except AttributeError:
        return None

def parse_organism(x):
    
    if x =='-':
        return(None,None)
    
    x = x.split('|')[1] if len(x.split('|')) > 1 else x

    organism_name = parse_interactor_type(x).replace('"','')
    organism_id = re.search('taxid:(-*\d+)', x).group(1)
    
    try:
        organism_id = int(organism_id)
    except ValueError:
        organism_id = organism_id
        
    return (organism_id, organism_name)
      
def parse_row(row):
    ##
    ## Parse interactor A data:
    ##
    parsed_row = {
        'interactor_A': row['#ID(s) interactor A'],
        'biological_role_A': parse_interactor_type(row['Biological role(s) interactor A']),
        'type_A': parse_interactor_type(row['Type(s) interactor A'])
    }

    organism_A = parse_organism(row['Taxid interactor A'])

    parsed_row['organism_A'] = organism_A[0]
    parsed_row['tax_id_A'] = organism_A[1]

    ##
    ## Parse interactor B data:
    ##
    parsed_row.update({
        'interactor_B': row['ID(s) interactor B'],
        'biological_role_B': parse_interactor_type(row['Biological role(s) interactor B']),
        'type_B': parse_interactor_type(row['Type(s) interactor B'])
    })

    organism_B = parse_organism(row['Taxid interactor B'])

    parsed_row['organism_B'] = organism_B[0]
    parsed_row['tax_id_B'] = organism_B[1]

    ##
    ## Parse interaction metadata
    ##

    parsed_row.update({
        'publication': row['Publication Identifier(s)'],
        'interaction_type': parse_interactor_type(row['Interaction type(s)']),
        'interaction_id': row['Interaction identifier(s)'].split('|')[0],
        'score': float(row['Confidence value(s)'].split(':')[1])
    })

    return parsed_row

def parse_network(filename):
    df = pd.read_csv(filename, sep='\t')

    network_parsed = df.apply(parse_row, axis=1)
    network_parsed_df = pd.DataFrame(network_parsed.tolist())

    return network_parsed_df

if __name__ == '__main__':

    # Parsing commandline arguments
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Networks tsv export file parser.')

    parser.add_argument('-i', '--input', help='Input file name.', type=str)
    parser.add_argument('-o', '--output', help='Output file name.', type=str)
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output

    # Open and parse input file:
    complex_table = parse_network(input_file)

    # Save output file:
    complex_table.to_csv(output_file, sep='\t', index=False)


