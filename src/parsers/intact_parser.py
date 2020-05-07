import pandas as pd
import argparse
import re


def parse_organism(x):
    """
    The taxonomy ID is returned based on the provided 'Taxid interactor' value eg. taxid:10090(mouse)|taxid:10090(Mus musculus)
    """
    
    if x =='-':
        return None
    
    x = x.split('|')[1] if len(x.split('|')) > 1 else x

    organism_id = re.search('taxid:(-*\d+)', x).group(1)
    return organism_id


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
    parser.add_argument('-m', '--mapfile', help='Uniprot ID map file.', type=str)
    args = parser.parse_args()

    network_file = args.input
    output_file = args.output
    id_map_file = args.mapfile

    # Open input file:
    network_df = pd.read_csv(network_file, sep='\t')

    # Open uniprot id mapping file:
    id_map_df = pd.read_csv(id_map_file, sep='\t', names=['uniprot','source','id'])
    id_map_df = id_map_df.loc[id_map_df.source == 'Ensembl']

    ##
    ## Parse various fields:
    ##

    # Parse taxonomy IDs:
    network_df['taxid_a'] = network_df['Taxid interactor A'].apply(parse_organism)
    network_df['taxid_b'] = network_df['Taxid interactor B'].apply(parse_organism)

    # Parse interaction identifier:
    network_df['interaction_id'] = (network_df['Interaction identifier(s)']
        .apply(lambda x: x.split('|')[0].replace('intact:','')))

    # Parse interactor id:
    network_df['id_a'] = network_df['#ID(s) interactor A'].apply(lambda x: x.split(':')[1].split('-PRO')[0])
    network_df['id_b'] = network_df['ID(s) interactor B'].apply(lambda x: x.split(':')[1].split('-PRO')[0])


    ##
    ## Filter data
    ##

    # Only these IDs will be considered from the complex portal data. 
    taxonomy_ids = ['2697049','694009','9606']

    # Filter out homologs:
    filtered_interact = network_df.loc[network_df['taxid_b'].isin(taxonomy_ids) &
                  network_df['taxid_a'].isin(taxonomy_ids)]

    # Filter out human/human interactions:
    filtered_interact = filtered_interact.loc[~((filtered_interact['taxid_b']=='9606') &
                  (filtered_interact['taxid_a'] == '9606'))]


    # Select a few columns:
    filtered_interact = filtered_interact[['interaction_id','id_a','id_b']]
    filtered_interact = filtered_interact.drop_duplicates()
    
    # Get unique list of interactors:
    interactors = filtered_interact.id_a.append( filtered_interact.id_b).unique()

    # aggregating interactors across IDs:
    aggregated_interactions = []
    for interactor in interactors:
        interaction_ids = filtered_interact.loc[(filtered_interact.id_a == interactor ) |
                      (filtered_interact.id_b == interactor),'interaction_id'].unique().tolist()
        
        aggregated_interactions.append({
            'uniprot_id': interactor,
            'Covid_direct_interactions': interaction_ids
        })
    
    # Get dataframe:
    aggregated_interactions_df = pd.DataFrame(aggregated_interactions)

    # Add ensembl gene identifiers when available:
    aggregated_interactions_df = aggregated_interactions_df.merge(id_map_df[['uniprot','id']], how='left', left_on='uniprot_id', right_on='uniprot')

    # Update id column when value is missing:
    aggregated_interactions_df['id'] = aggregated_interactions_df.apply(lambda x: x['id'] if x['id'] == x['id'] else x['uniprot_id'], axis=1)
    
    # Drop unwanted columns:
    aggregated_interactions_df.drop(['uniprot_id','uniprot'], inplace=True, axis=1)
    
    # Save output file:
    aggregated_interactions_df.to_csv(output_file, sep='\t', index=False)


