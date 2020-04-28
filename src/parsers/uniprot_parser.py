#!/usr/bin/env python3

import argparse
import json 
import requests
import pandas as pd 


def map_primary_uniprot_accession_to_ensembl(row):
    organism = row['organism_scientific_name'].replace(' ','_').lower()
    accession = row['primaryAccession']
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
    """
    Reading Uniprot JSON files.
    """

    # Reading arguments
    parser = argparse.ArgumentParser(description='Parse uniprot .json file')
    parser.add_argument('-i','--inputfile',required=True, dest="UNIPROT_IN", type=str, help='input uniprot dat file to parse')
    parser.add_argument('-o','--outputfile',required=True, dest="UNIPROT_OUT", type=str, help='Parsed tsv file name.')

    args = parser.parse_args()
    uniprot_file = args.UNIPROT_IN
    outputFile = args.UNIPROT_OUT

    # Open json file:
    with open(uniprot_file) as f:
        uniprot_data = json.load(f)

    # Parsing json data:
    parsed_entries= []
    for entry in uniprot_data['results']:

        # Pick simle pieces:
        parsed_entry = {
            'primaryAccession': entry['primaryAccession'],
            'uniprot_name': entry['uniProtkbId'],
            'organism_name': entry['organism']['commonName'],
            'organism_id': entry['organism']['taxonId'],
            'organism_scientific_name': entry['organism']['scientificName']
        }
        
        # Seconday accessions might not provided:
        parsed_entry['secondaryAccessions'] = ','.join(entry['secondaryAccessions']) if 'secondaryAccessions' in entry else None
        
        # Adding parsed data:
        parsed_entries.append(parsed_entry)
        
    # Format data into dataframe:
    parsed_entries_df = pd.DataFrame(parsed_entries)

    # Mapping primary uniprot accessions to Ensembl gene id:
    print('[Info] Mapping primary Uniprot identifiers to Ensembl gene id...')
    parsed_entries_df['gene_id'] = parsed_entries_df.apply(map_primary_uniprot_accession_to_ensembl, axis=1)

    # Save file:
    parsed_entries_df.to_csv(outputFile, sep='\t', index=False)


if __name__ == '__main__':
    main()


