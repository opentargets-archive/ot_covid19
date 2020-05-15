import pandas as pd
import argparse
import logging

class TargetActiveCompounds():

    def __init__(self):

        # Configure logging
        # Create logger
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

        # Add formatter to ch
        ch.setFormatter(formatter)

        # Add ch to handler
        self._logger.addHandler(ch)

        # Dictionaries for storing safety info and gene name to Ensembl id mappings
        self.target_compound_activity_info = {}
        self.target_uniprot2ensembl_map = {}

    def get_uniprot2ensembl_mappings(self, filename):
        """Return a dictionary that maps UniProt ids to Ensembl ids"""

        # Load UniProt to Ensembl mapping file an iterate through every protein
        id_map_df = pd.read_csv(filename, sep='\t', header=0)

        for index, row in id_map_df.iterrows():
            if row['uniprot_id'] in self.target_uniprot2ensembl_map:
                self.target_uniprot2ensembl_map[row['uniprot_id']].append(row['ensembl_id'])
            else:
                self.target_uniprot2ensembl_map[row['uniprot_id']] = [row['ensembl_id']]

        self._logger.info("{} UniProt ids mapped to Ensembl".format(len(self.target_uniprot2ensembl_map)))

    def parse_target_compound_activity(self, uniprot_mapping_file, activity_file, output_file):

        # Load Uniprot id to Ensembl id mappings
        self.get_uniprot2ensembl_mappings(uniprot_mapping_file)

        # Read activity file and extract info
        activity_df = pd.read_csv(activity_file, sep='\t', header=0, index_col=0)
        for uniprot_id, info in activity_df.iterrows():
            for gene in self.target_uniprot2ensembl_map[uniprot_id]:
                if gene in self.target_compound_activity_info:
                    self.target_compound_activity_info[gene]['active_invitro_drugs'].append(info['molecule_chembl_id'])
                else:
                    self.target_compound_activity_info[gene] = { 'active_drug_covid_invitro_assay': True,
                                                                 'active_invitro_drugs': [info['molecule_chembl_id']]}

        self._logger.info("Activity info parsed for {} targets".format(len(self.target_compound_activity_info)))
        # Write to tsv file
        target_activity_df = pd.DataFrame.from_dict(self.target_compound_activity_info, orient='index', columns=['active_drug_covid_invitro_assay', 'active_invitro_drugs'])
        target_activity_df.index.name = "id"
        target_activity_df.to_csv(output_file, sep='\t')

def main():

    # Parse CLI parameters
    parser = argparse.ArgumentParser(description='Parse compounds that are active against COVID-19 in in-vitro assays.')
    parser.add_argument('-i','--inputFile',
                        help='Name of TSV/TAB file with compound COVID-19 activity information',
                        type=str, default='actives_covid_table_final.txt')

    parser.add_argument('-m', '--mappingFile',
                        help='Name of UniProt to Ensembl mapping file',
                        type=str, default='ensembl_parsed.json.gz')

    parser.add_argument('-o','--output',
                        help='Output file name',
                        type=str, default='target_active_covid_compounds.tsv')

    args = parser.parse_args()

    # Get parameters:
    input_file = args.inputFile
    mapping_file = args.mappingFile
    output_file = args.output

    target_active_compounds = TargetActiveCompounds()
    target_active_compounds.parse_target_compound_activity(mapping_file, input_file,  output_file)


if __name__ == '__main__':
    main()
