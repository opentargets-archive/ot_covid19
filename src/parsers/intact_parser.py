import pandas as pd
import argparse
import re
import json



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


def get_direct_interactors(input_df):
    """
    This function reads the covid19 intact release

    Output: pd.DataFrame
    id: uniprot identifiers
    Covid_direct_interactions: Intact network identifiers
    """

    # Only these IDs will be considered from the complex portal data. 
    taxonomy_ids = ['2697049','694009','9606']
    
    # Filter out homologs:
    filtered_interact = network_df.loc[network_df['taxid_b'].isin(taxonomy_ids) &
                  network_df['taxid_a'].isin(taxonomy_ids)]

    # Filter out human/human interactions:
    filtered_interact = filtered_interact.loc[~((filtered_interact['taxid_b']=='9606') &
                  (filtered_interact['taxid_a'] == '9606'))]


    # Select a few columns:
    filtered_interact = filtered_interact.drop_duplicates()
    
    # Get unique list of interactors:
    interactors = filtered_interact.id_a.append( filtered_interact.id_b).unique()

    # aggregating interactors across IDs:
    aggregated_interactions = []
    for interactor in interactors:
        interaction_ids = filtered_interact.loc[(filtered_interact.id_a == interactor ) |
                      (filtered_interact.id_b == interactor),'interaction_id'].unique().tolist()
        
        # Get taxonomy id of the interactor:
        try:
            tax_id = filtered_interact.loc[ filtered_interact.id_a == interactor ].taxid_a.tolist()[0]
        except:
            tax_id = filtered_interact.loc[ filtered_interact.id_b == interactor ].taxid_b.tolist()[0]
        
        aggregated_interactions.append({
            'uniprot_id': interactor,
            'Covid_direct_interactions': interaction_ids,
            'tax_id': tax_id
        })
    
    # Return dataframe:
    return pd.DataFrame(aggregated_interactions)
    

def get_second_level_interactions(indirect_interactions_list, human_interactions_df):
    """

    """

    # Filter interactions between direct interactors and other proteins (~42k):
    second_level_interactions = human_interactions_df.loc[
                                    (human_interactions_df.interactor_a.isin(indirect_interactions_list)) |
                                    (human_interactions_df.interactor_b.isin(indirect_interactions_list))
                                ]
    # 
    secondary_interactions = {}
    for index, row in second_level_interactions.iterrows():
        if row['interactor_a'] in indirect_interactions_list and row['interactor_b'] in indirect_interactions_list:
            # Adding interactor A:
            try:
                secondary_interactions[row['interactor_a']] += row['interaction_identifier']
            except: 
                secondary_interactions[row['interactor_a']] = row['interaction_identifier']

            # Adding interactor B:
            try:
                secondary_interactions[row['interactor_b']] += row['interaction_identifier']
            except: 
                secondary_interactions[row['interactor_b']] = row['interaction_identifier']

        elif row['interactor_a'] in indirect_interactions_list:
            # Adding interactor B:
            try:
                secondary_interactions[row['interactor_b']] += row['interaction_identifier']
            except: 
                secondary_interactions[row['interactor_b']] = row['interaction_identifier'] 

        elif row['interactor_b'] in indirect_interactions_list:
            # Adding interactor A:
            try:
                secondary_interactions[row['interactor_a']] += row['interaction_identifier']
            except: 
                secondary_interactions[row['interactor_a']] = row['interaction_identifier'] 

    # Return dataframe with indirect interactions:        
    return pd.DataFrame({'uniprot_id': list(secondary_interactions.keys()), 
                       'Covid_indirect_interactions': list(secondary_interactions.values())})


def get_all_implicated_interactions(network_df):
    implicated_df = pd.concat([
        network_df[['id_a','taxid_a']].rename(columns={'id_a':'uniprot_id','taxid_a':'taxid'}),
        network_df[['id_b','taxid_b']].rename(columns={'id_b':'uniprot_id','taxid_b':'taxid'})
    ]).drop_duplicates()

    implicated_df = implicated_df.loc[implicated_df.taxid=='9606'].drop('taxid', axis=1)
    implicated_df['Implicated_in_viral_infection'] = True

    return implicated_df


def map_to_ensembl_gene_id(merged, id_map_df):
    
    # Add ensembl gene identifiers when available:
    merged = merged.merge(id_map_df[['uniprot','id']], how='left', left_on='uniprot_id', right_on='uniprot')

    # Update id column when value is missing:
    merged['id'] = merged.apply(lambda x: x['id'] if x['id'] == x['id'] else x['uniprot_id'], axis=1)
    
    # Drop unwanted columns:
    return merged.drop(['uniprot_id','uniprot'], axis=1)


def read_human_interactions(human_interactions_file):
    """
    Based on the Intact JSON dump file, a dataframe is built with all 
    human protein-protein interactions.

    Columns:
    interactor_a str uniprot id
    interactor_b str uniprot id
    interaction_identifier str intact id
    """

    all_human_interactions = []
    with open(human_interactions_file,'r') as f:
        for line in f:
            interaction = json.loads(line)

            if interaction["mi_score"] is None:
                continue

            # Applying MI score threshold for interactions:
            if interaction["mi_score"] > .45:

                all_human_interactions.append({
                    'interactor_a':interaction['interactorA_uniprot_name'].split('-')[0],
                    'interactor_b':interaction['interactorB_uniprot_name'].split('-')[0],
                    'interaction_identifier': interaction['interaction_identifier']
                })

    # return dataframe with all human interactions (~520k)
    return pd.DataFrame(all_human_interactions)


def read_and_filter_covid_interactions(network_file):

    # Reading tsv file:
    network_df = pd.read_csv(network_file, sep='\t')

    # Parse taxonomy IDs:
    network_df['taxid_a'] = network_df['Taxid interactor A'].apply(parse_organism)
    network_df['taxid_b'] = network_df['Taxid interactor B'].apply(parse_organism)

    # Parse interaction identifier:
    network_df['interaction_id'] = (network_df['Interaction identifier(s)']
        .apply(lambda x: x.split('|')[0].replace('intact:','')))

    # Parse interactor id:
    network_df['id_a'] = network_df['#ID(s) interactor A'].apply(lambda x: x.split(':')[1].split('-PRO')[0])
    network_df['id_b'] = network_df['ID(s) interactor B'].apply(lambda x: x.split(':')[1].split('-PRO')[0])

    return network_df[['id_a','taxid_a','id_b','taxid_b','interaction_id']]


def read_and_filter_uniprot_map_file(id_map_file):
    id_map_df = pd.read_csv(id_map_file, sep='\t', names=['uniprot','source','id'])
    return id_map_df.loc[id_map_df.source == 'Ensembl']


if __name__ == '__main__':

    # Parsing commandline arguments
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Networks tsv export file parser.')

    parser.add_argument('-i', '--input', help='Input file name.', type=str)
    parser.add_argument('-o', '--output', help='Output file name.', type=str)
    parser.add_argument('-f', '--full', help='Human interactions file name.', type=str)
    parser.add_argument('-m', '--mapfile', help='Uniprot ID map file.', type=str)
    args = parser.parse_args()

    network_file = args.input
    output_file = args.output
    id_map_file = args.mapfile
    human_interactions = args.full

    ##
    ## Reading input files:
    ##

    # Reading human interactions:
    print('[Info] Reading all human interactions...')
    human_interactions_df = read_human_interactions(human_interactions)

    # Reading id mapping file:
    print('[Info] Reading and filtering uniprot mapfile...')
    id_map_df = pd.read_csv(id_map_file, sep='\t', names=['uniprot','source','id'])
    id_map_df = id_map_df.loc[id_map_df.source == 'Ensembl']

    # Reading covid network file:
    print('[Info] Reading and filtering COVID related interactions...')
    network_df = read_and_filter_covid_interactions(network_file)

    ##
    ## Process data:
    ##
    
    # Get direct interactors:
    print('[Info] Generating table with direct interactors of COVID proteins...')
    direct_interactions_df = get_direct_interactors(network_df)

    # Get a unique list of uniprot IDs of direct interactors:
    indirect_interactions_list = direct_interactions_df.loc[direct_interactions_df.tax_id == '9606'].uniprot_id.tolist()

    # Get indirect interactors:
    print('[Info] Generating table with indirect interactors of COVID proteins...')
    indirect_interactions_df = get_second_level_interactions(indirect_interactions_list, human_interactions_df)

    # Mark any human proteins implicated in viral pathogenesis:
    print('[Info] Generating table with human proteins implicated in viral infection...')
    implicated_proteins = get_all_implicated_interactions(network_df)

    ##
    ## Merge and save:
    ##

    # Merging data together:
    print('[Info] Merging tables together...')
    merged = direct_interactions_df.drop(['tax_id'], axis=1).merge(indirect_interactions_df, on='uniprot_id', how='outer')
    merged = merged.merge(implicated_proteins, on='uniprot_id', how='outer')
    merged['Implicated_in_viral_infection'] = merged['Implicated_in_viral_infection'].apply(lambda x: x if x is True else False)

    # Adding Ensembl IDs:
    print('[Info] Adding Ensembl gene IDs.')
    final_df = map_to_ensembl_gene_id(merged,id_map_df)

    # Save output file:
    final_df.to_csv(output_file, sep='\t', index=False)


