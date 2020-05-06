import argparse
import pandas as pd 

def get_target_druginfo(df):
    """ Get number of drugs per target and max phase"""

    result = df \
        .groupby('id').agg(
        max_phase=('phase', 'max'),
        drugs_in_clinic=('drug_id', 'nunique')
        ) \
        .reset_index()

    return result

def get_drug_info(df):
    """ Get max phase per drug"""

    result = df \
        .groupby('drug_id').agg(
        max_phase=('phase', 'max')
        ) \
        .reset_index()

    return result

def main():
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Parse information from OT drug evidence and aggregates info at the target level.')

    parser.add_argument('-i', '--input', help='OT drug evidence table', required=True, type=str)
    parser.add_argument('-o', '--output', help='Output file name.', required=True, type=str)
    parser.add_argument('-e', '--entity', help='Entity type to extract info for.', required=True, choices=['target', 'drug'])

    args = parser.parse_args()

    # Get parameters:
    input_file = args.input
    output_file = args.output
    entity = args.entity

    df = pd.read_csv(input_file, \
                sep = "\t", \
                names = ["id", "disease_id", "drug_id", "phase", "moa", "drug_name"])

    if entity == "target":
        result = get_target_druginfo(df)
    else:
        result = get_drug_info(df)

    result.to_csv(output_file, sep='\t', index=False)

if __name__ == '__main__':
    main()
