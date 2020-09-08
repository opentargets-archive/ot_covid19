import pandas as pd
import json
import gzip
import argparse


def get_ensembl_gene_set(ensembl_file):
    
    data = []

    # Reading ensembl json file:
    with gzip.open(ensembl_file) as f:
        for line in f:
            data.append(json.loads(line))
            
    df = pd.DataFrame(data)
    return df[['id','name']]
    

def table_formatter(row):

    ## Generating field for MR data:
    
    # Formatting dataset description:
    dataset = row['COVID_dataset'].replace('_',' ')
    dataset = dataset.replace('covid', f'covid (N={row["n_cases"]:,})',1)
    dataset = dataset + f" (N={row['n_controls']:,})"
    dataset = dataset.capitalize()
    
    # Round p-value:
    pval = round(row['pval'],3) if row['pval'] > 0.01 else f'{row["pval"]:.2E}'
    
    mr_data = { 
        'Dataset': dataset,
        'Number of SNPs': row['nSNPs'],
        'MR estimate': round(row['MR_estimate'],3),
        'Lower conf.int': round(row['lower_ci'],3),
        'Upper conf.int': round(row['upper_ci'],3),
        'p-value': pval
    }
    
    # Generate field for colocalization:
    coloc_data = {
        'Colocalising SNP': row['colocalising_SNP'],
        'Prosterior probability': row['coloc_posterior_probability_H4']
    }
    
    # Initialize return value:
    returnvalue = {
        'gene_name': row['Gene_or_Protein'].split('_')[0],
        'MR_field': mr_data,
        'colocalization': coloc_data
    }
    
    return returnvalue


def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='This script parses the Mendelian randomization table.')

    parser.add_argument('-i', '--input', help='CSV with the MR table.', required=True, type=str)
    parser.add_argument('-o', '--output', help='Output tsv file of the parsed MR data.', required=True, type=str)
    parser.add_argument('-e', '--ensembl', help='Parsed ensembl file for gene name mapping.', required=True, type=str)

    args = parser.parse_args()
    mr_file = args.input
    mr_file_parsed = args.output 
    es_file = args.ensembl

    # Get dataframe for ID mapping:
    print('[Info] Reading list of Ensembl genes.')
    ensembl_df = get_ensembl_gene_set(es_file)

    # Reading MR dataset:
    print('[Info] Reading table with the results of MR.')
    mr_df = pd.read_csv(mr_file, sep=',')

    # We need to check if all required columns are in the csv. 
    # This step is here to ensure the headers won't change after updating the table.
    required_columns = pd.Series(['Gene_or_Protein',
         'nSNPs',
         'COVID_dataset',
         'n_cases',
         'n_controls',
         'MR_estimate',
         'lower_ci',
         'upper_ci',
         'pval',
         'colocalising_SNP',
         'coloc_posterior_probability_H4'
    ])

    if not required_columns.isin(mr_df.columns.tolist()).all():
        missing_columns = ', '.join(required_columns.loc[~required_columns.isin(mr_df.columns.tolist())].tolist())
        raise ValueError(f'Some of the required columns of the input table is missing. Missing columns: {missing_columns}')

    # Format data:
    print('[Info] Formatting data.')
    formatted_data = mr_df.apply(table_formatter, axis=1)
    MR_formatted_df= pd.DataFrame(formatted_data.tolist())

    # Merge tables:
    print('[Info] Adding Ensembl gene IDs to table and save.')
    merged = ensembl_df.merge(MR_formatted_df, how='inner', left_on='name', right_on='gene_name')

    # As the id column is not unique, we have to pool the MR results:
    pooled_data = []
    for gene_id, group in merged.groupby('id'):
        pooled_data.append({
            'id': gene_id,
            'MR_field': json.dumps(group.MR_field.tolist()),
            'colocalisation': json.dumps(group.colocalization.tolist())
        })

    pooled_df = pd.DataFrame(pooled_data)
    
    # Save data:
    pooled_df.to_csv(mr_file_parsed, sep='\t', index=False, doublequote=False, quotechar="'")


if __name__ == '__main__':
    main()
