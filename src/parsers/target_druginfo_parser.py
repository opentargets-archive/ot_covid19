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

def main():
    
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Parse information from OT drug evidence and aggregates info at the target level.')

    parser.add_argument('-i', '--input', help='OT drug evidence table', required=True, type=str)
    parser.add_argument('-o', '--output', help='Output file name.', required=True, type=str)

    args = parser.parse_args()

    # Get parameters:
    input_file = args.input
    output_file = args.output

    df = pd.read_csv(input_file, \
                sep = "\t", \
                names = ["id", "disease_id", "drug_id", "phase", "moa", "drug_name"])

    # result = df \
    #     .groupby('id').agg(
    #         max_phase = ('phase', 'max'),
    #         drugs_in_clinic = ('drug_id', 'nunique')
    #     ) \
    #     .reset_index()

    result = get_target_druginfo(df)

    result.to_csv(output_file, sep='\t', index=False)

if __name__ == '__main__':
    main()
