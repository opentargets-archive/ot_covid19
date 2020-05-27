import json
import gzip
import argparse
import pandas as pd 

def main():
    
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Parse information from HPA json export and saves as CSV.')

    parser.add_argument('-i', '--input', help='HPA JSON input file name.', required=True, type=str)
    parser.add_argument('-o', '--output', help='Output file name.', required=True, type=str)

    args = parser.parse_args()

    # Get parameters:
    input_file = args.input
    output_file = args.output

    parsed_entries = []
    with open(input_file, "r") as f:
        for line in f:
            entry = json.loads(line)
            parsed_entry = {
                'id': entry['Ensembl'],
                'hpa_subcellular_location': entry['Subcellular location'],
                'hpa_rna_tissue_distribution': entry['RNA tissue distribution'],
                'hpa_rna_tissue_specificity': entry['RNA tissue specificity'],
            }
            parsed_entry['hpa_rna_specific_tissues'] = list(entry['RNA tissue specific NX'].keys()) if entry['RNA tissue specific NX'] is not None  else None
            parsed_entries.append(parsed_entry)

    parsed_entries_df = pd.DataFrame(parsed_entries)

    # save columns in JSON format:
    for column in ['hpa_rna_specific_tissues', 'hpa_subcellular_location']:
        parsed_entries_df[column] = parsed_entries_df[column].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)

    # Save file:
    parsed_entries_df.to_csv(output_file, sep='\t', index=False)

if __name__ == '__main__':
    main()
