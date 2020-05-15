import pandas as pd
import argparse


if __name__ == '__main__':

    # Parsing commandline arguments
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Script to generate the most complete set of Uniprot ID - Ensembl ID map.')

    parser.add_argument('-e', '--ensembl_map', help='Ensembl input file name.', type=str)
    parser.add_argument('-u', '--uniprot_map', help='Uniprot input file name.', type=str)
    parser.add_argument('-o', '--output', help='Output file name.', type=str)

    args = parser.parse_args()

    ensembl_mapfile = args.ensembl_map
    uniprot_mapfile = args.uniprot_map
    output_file = args.output

    ##
    ## Reading input files:
    ##
    
    uniprot_map_df = pd.read_csv(uniprot_mapfile, sep='\t', names=['uniprot','source','id'])
    ensembl_map_df = pd.read_csv(ensembl_mapfile, sep='\t')

    ## Report input data:
    print('[Info] Report on the Ensembl mapping file:')
    print('[Info] Number of rows: {}'.format(len(ensembl_map_df)))
    print('[Info] Number of unique genes: {}'.format(len(ensembl_map_df.ensembl_id.unique())))
    print('[Info] Number of unique proteins: {}'.format(len(ensembl_map_df.uniprot_id.unique())))
    print('')
    print('[Info] Report on the Uniprot mapping file:')
    print('[Info] Number of unique proteins: {}'.format(len(uniprot_map_df.uniprot.unique())))
    uniprot_map_df = uniprot_map_df.loc[uniprot_map_df.source == 'Ensembl']
    print('[Info] Number of Ensembl genes with mapped proteins: {}'.format(len(uniprot_map_df.uniprot.unique())))
    print('[Info] Number of genes mapped to proteins: {}'.format(len(uniprot_map_df.id.unique())))

    ## Merging dataframes:
    print('\n[Info] Merging the two datasets...')
    uniprot_map_df = uniprot_map_df.drop(['source'], axis=1).rename(columns={"uniprot":"uniprot_id","id":"ensembl_id"})
    merged = pd.concat([uniprot_map_df, ensembl_map_df])
    merged = merged.drop_duplicates()

    print('[Info] Number of unique mappings in the merged dataset: {}'.format(len(merged)))
    print('[Info] Number of proteins mapped to Ensembl genes: {}'.format(len(merged.uniprot_id.unique())))
    print('[Info] Number of genes mapped to proteins: {}'.format(len(merged.ensembl_id.unique())))

    # Save output file:
    merged.to_csv(output_file, sep='\t', index=False)


