import argparse
import pandas as pd
import requests
pd.options.mode.chained_assignment = None # Supressing chain copy warnings


# Function to map uniprot accessions to ensembl gene IDs.
def map_primary_uniprot_accession_to_ensembl(accession, organism = 'homo_sapiens'):

    URL = 'http://rest.ensembl.org/xrefs/symbol/{}/{}?content-type=application/json&object_type=gene'.format(
        organism,accession)

    response = requests.get(URL).json()

    if 'error' in response:
        print('[Warning] Could not find Ensembl gene ID to {}'.format(accession))
        return None
    
    try:
        return response[0]['id'] if len(response) > 0 else None
    except:
        return None


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='This script parses complex portal data data.')

    parser.add_argument('-i', '--input', help='Complexportal COVID-19 tsv file.', required=True, type=str)
    parser.add_argument('-o', '--output', help='Output tsv file of the parsed complexportal file.', required=True, type=str)

    args = parser.parse_args()
    input_complex_file = args.input
    output_parsed_file = args.output 

    complex_df = pd.read_csv(input_complex_file, sep='\t')

    # Drop rows with complex:
    complex_df.drop(complex_df.loc[complex_df.component_id.str.match('CPX')].index, inplace=True)

    # Update component ID:
    complex_df['component_id'] = complex_df.component_id.apply(lambda x: x.split('-')[0])

    # Pool components:
    complexes = []
    for component_id, group in complex_df.groupby(['component_id']):
        complex_names = group.complex_name.unique().tolist()
        
        # Looking up ensembl gene id:
        ensembl_id = map_primary_uniprot_accession_to_ensembl(component_id) if map_primary_uniprot_accession_to_ensembl(component_id) else component_id
        complexes.append({
            'id': ensembl_id,
            'COVID_complex_names': complex_names
        })
        
    covid_complexes = pd.DataFrame(complexes)
    covid_complexes.to_csv(output_parsed_file, sep='\t', index=False)

if __name__ == '__main__':
    main()
