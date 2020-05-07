import argparse
import pandas as pd
import numpy as np

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

def get_toy_covid_ct_table(df):
    """ Create an example table of drugs in clinical trials for COVID-19
    It will select 500 random drugs and assign them a random phase"""

    toy_covid_ct_list = []

    drugs = df.drug_id.unique()
    random_drugs = np.random.choice(drugs, 500, replace=False)

    for drug in drugs:
        if drug in random_drugs:
            covid19_ct = True
            covid19_ct_phase = int(np.random.choice([1,2,3,4], 1))
        else:
            covid19_ct = False
            covid19_ct_phase = None
        toy_covid_ct_list.append(dict(id=drug, has_covid19_trial=covid19_ct, covid19_trial_phase=covid19_ct_phase))

    return pd.DataFrame(toy_covid_ct_list)

def main():
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Parse information from OT drug evidence and aggregates info at the target level.')

    parser.add_argument('-i', '--input', help='OT drug evidence table', required=True, type=str)
    parser.add_argument('-o', '--output', help='Output file name.', required=True, type=str)
    parser.add_argument('-e', '--entity', help='Entity type to extract info for.', required=True, choices=['target', 'drug', 'covid19_trials'])

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
    elif entity == "drug":
        result = get_drug_info(df)
    else:
        result = get_toy_covid_ct_table(df)
        # Convert clinical trials phase column to an integer format that supports missing values
        result['covid19_trial_phase'] = result['covid19_trial_phase'].astype('Int64')

    result.to_csv(output_file, sep='\t', index=False)

if __name__ == '__main__':
    main()
