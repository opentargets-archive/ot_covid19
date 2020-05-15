import json
import gzip
import argparse

def parsing_ensembl_json(data):
    """
    Parsing relevant fields from ensembl json data
    """

    parsed_data = {}
    # cica = 'pocok' if 1 < 3  else None
    parsed_data['id'] = data['id'] if 'id' in data else None
    parsed_data['ensembl_id'] = data['id'] if 'id' in data else None
    parsed_data['biotype'] = data['biotype'] if 'biotype' in data else None
    parsed_data['name'] = data['name'] if 'name' in data else None
    parsed_data['taxon_id'] = data['taxon_id'] if 'taxon_id' in data else None
    parsed_data['PDB'] = data['PDB'] if 'PDB' in data else []
    parsed_data['description'] = data['description'] if 'description' in data else None
    parsed_data['MIM_morbidity'] = get_MIM_morbidity(data['xrefs']) if 'xrefs' in data else []

    # Parsing uniprot names:
    parsed_data['uniprot_ids'] = get_uniprot_ids(data)

    return parsed_data


def get_uniprot_ids(data):
    ids = []
    
    if 'Uniprot_gn' in data:
        ids += data['Uniprot_gn']
    if 'Uniprot/SPTREMBL' in data:
        ids += data['Uniprot/SPTREMBL']
    if 'Uniprot/SWISSPROT' in data:
        ids += data['Uniprot/SWISSPROT']
        
    ids = list(set(ids))
    
    return ids


def get_MIM_morbidity(xrefs):
    morbidities = []
    for xref in xrefs:
        if xref['dbname'] == 'MIM_MORBID':
            morbidities.append({
              'display_id': xref['display_id'],
              'primary_id': xref['primary_id']
            })
            
    return morbidities


def main():
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Parse information from Ensembl json export and saves as gzipped json.')

    parser.add_argument('-i', '--input', help='Ensembl JSON input file name.', required=True, type=str)
    parser.add_argument('-o', '--output', help='Output file name.', required=True, type=str)

    args = parser.parse_args()

    # Get parameters:
    input_file = args.input
    output_file = args.output

    # Open output gzip file.
    output_file_handle = gzip.open(output_file, 'wt')

    # OPen and looping through all ensembl genes:
    with open(input_file, 'r') as i:
        for line in i:        
            # Read data:
            try:
                data = json.loads(line.strip())
                
                # Parse fields:
                parsed_data = parsing_ensembl_json(data)
                
                # Save parsed field:
                output_file_handle.write(json.dumps(parsed_data)+'\n')
                
            except:
                raise
                
    output_file_handle.close()



if __name__ == '__main__':
    main()
