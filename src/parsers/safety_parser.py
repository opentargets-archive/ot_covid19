import json
import gzip
import pandas as pd
import argparse
import logging

class Safety():

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
        self.target_safety_info = {}
        self.gene_name2ensembl_map = {}

    def get_gene_name2ensembl_mappings(self, filename):
        """Return a dictionary that maps gene names to Ensembl ids"""

        # Load gene info file an iterate through every gene
        with gzip.open(filename, 'rt') as gene_file:
            for line in gene_file:
                gene_info_dict = json.loads(line.strip())
                if gene_info_dict['name'] in self.gene_name2ensembl_map:
                    self.gene_name2ensembl_map[gene_info_dict['name']].append(gene_info_dict['ensembl_id'])
                else:
                    self.gene_name2ensembl_map[gene_info_dict['name']] = [gene_info_dict['ensembl_id']]


    def build_json_safety(self, filename):
        """ Read known target safety file and create dictionary with affected organs"""

        with open(filename, 'r') as known_safety:
            known_safety_data = json.load(known_safety)
            for gene, liabilities in known_safety_data.items():
                affected_systems = set()
                # Targets may contain "adverse_effects" and/or "safety_risk_info"
                for liability_type, info in liabilities.items():
                    for effects in info:
                        for system in effects['organs_systems_affected']:
                            # Use mapped term unless this is an empty string, e.g. for "development", in such case use the term in the paper
                            if system['mapped_term']:
                                affected_systems.add(system['mapped_term'])
                            else:
                                self._logger.warning("The organ system \"{}\" in target {} is not mapped to uberon, using this term instead".format(system['term_in_paper'], gene))
                                affected_systems.add(system['term_in_paper'])
                if gene in self.gene_name2ensembl_map:
                    for ensembl_id in self.gene_name2ensembl_map[gene]:
                        if ensembl_id in self.target_safety_info:
                            self.target_safety_info[ensembl_id]['safety_organs_systems_affected'].update(affected_systems)
                        else:
                            self.target_safety_info[ensembl_id] = {'name': gene,
                                                                   'has_safety_risk': True,
                                                                   'safety_organs_systems_affected': list(affected_systems),
                                                                   'safety_info_source' : ["known_target_safety"]}

    def build_json_experimental_toxicity(self, filename):
        """Read experimental toxicity file and output gene ids, leaving "name" and "organs_systems_affected" empty"""

        experimental_toxicity_df = pd.read_csv(filename, sep='\t', header=0, index_col=0)
        for ensembl_gene_id, info in experimental_toxicity_df.iterrows():
            if ensembl_gene_id in self.target_safety_info:
                if 'experimental_toxicity' not in self.target_safety_info[ensembl_gene_id]['safety_info_source']:
                    self.target_safety_info[ensembl_gene_id]['safety_info_source'].append("experimental_toxicity")
            else:
                self.target_safety_info[ensembl_gene_id] = { 'has_safety_risk' : True,
                                                             'name' : "N/A",
                                                             'safety_organs_systems_affected' : "N/A",
                                                             'safety_info_source' : ["experimental_toxicity"]
                                                             }

    def add_targets_without_safety_info(self, filename):
        """Add targets without target safety information to table"""

        # Load gene info file an iterate through every gene
        with gzip.open(filename, 'rt') as gene_file:
            for line in gene_file:
                gene_info_dict = json.loads(line.strip())
                if gene_info_dict['ensembl_id'] not in self.target_safety_info:
                    self.target_safety_info[gene_info_dict['ensembl_id']] = { 'has_safety_risk' : False,
                                                                              'name' : "N/A",
                                                                              'safety_organs_systems_affected' : "N/A",
                                                                              'safety_info_source' : "N/A"
                                                                              }


    def parse_safety(self, known_safety_file, experimental_toxicity_file , compressed_gene_file, output_filename, output_all):

        # Load gene name to Ensembl id mappings
        self.get_gene_name2ensembl_mappings(compressed_gene_file)

        # Extract needed information from known target safety file
        self.build_json_safety(known_safety_file)

        # Extract needed information from experimental toxicity file
        self.build_json_experimental_toxicity(experimental_toxicity_file)

        # Include all targets in output file if flag is set.
        # This is useful to have a more readable output after integration
        if output_all:
            self._logger.info("Outputting all targets")
            self.add_targets_without_safety_info(compressed_gene_file)

        # Write to tsv file
        safety_df = pd.DataFrame.from_dict(self.target_safety_info, orient='index', columns=['name', 'has_safety_risk', 'safety_info_source', 'safety_organs_systems_affected'])
        safety_df.index.name = "id"

        # save columns in JSON format:
        for column in ['safety_info_source', 'safety_organs_systems_affected']:
            safety_df[column] = safety_df[column].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)

        safety_df.to_csv(output_filename, sep='\t')

def main():

    # Parse CLI parameters
    parser = argparse.ArgumentParser(description='Parse known target safety and eperimental toxicity files and report the genes with safety information and the affected organs if available.')
    parser.add_argument('-k','--knownTargetSafetyFile',
                        help='Name of JSON file with known target safety information',
                        type=str, default='ot_know_target_safety.json')

    parser.add_argument('-e','--experimentalToxicityFile',
                        help='Name of TSV/TAB file with experimental toxicity information',
                        type=str, default='ot_experimental_toxicity.tsv')

    parser.add_argument('-g', '--geneFile',
                        help='Name of file with gene information',
                        type=str, default='ensembl_parsed.json.gz')

    parser.add_argument('-o','--output',
                        help='Output file name',
                        type=str, default='target_safety.tsv')
    parser.add_argument('-a', '--allTargets', help='Output all targets and not only the ones with safety information', action='store_true')

    args = parser.parse_args()

    # Get parameters:
    known_safety_file = args.knownTargetSafetyFile
    experimental_toxicity_file = args.experimentalToxicityFile
    gene_file = args.geneFile
    output_file = args.output
    output_all_targets = args.allTargets

    safety = Safety()
    safety.parse_safety(known_safety_file, experimental_toxicity_file, gene_file, output_file, output_all_targets)


if __name__ == '__main__':
    main()
