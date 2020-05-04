import json
import gzip
import pandas as pd
import argparse
import logging

class Safety():

    def __init__(self):
        self._logger = logger = logging.getLogger(__name__)
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
                # Targets may contain "andverse_effects" and/or "safety_risk_info"
                for liability_type, info in liabilities.items():
                    for effects in info:
                        for system in effects['organs_systems_affected']:
                            affected_systems.add(system['mapped_term'])
                if gene in self.gene_name2ensembl_map:
                    for ensembl_id in self.gene_name2ensembl_map[gene]:
                        if ensembl_id in self.target_safety_info:
                            self.target_safety_info[ensembl_id]['organs_systems_affected'].update(affected_systems)
                        else:
                            self.target_safety_info[ensembl_id] = {'name': gene,
                                                     'safety_risk': True,
                                                     'organs_systems_affected': list(affected_systems)}

    def build_json_experimental_toxicity(self, filename):
        """Read experimental toxicity file and output gene ids, leaving "name" and "organs_systems_affected" empty"""

        experimental_toxicity_df = pd.read_csv(filename, sep='\t', header=0, index_col=0)
        for ensembl_gene_id, info in experimental_toxicity_df.iterrows():
            if ensembl_gene_id not in self.target_safety_info:
                self.target_safety_info[ensembl_gene_id] = { 'safety_risk' : True,
                                                             'name' : "N/A",
                                                             'organs_systems_affected' : "N/A"
                                                             }



    def parse_safety(self, known_safety_file, experimental_toxicity_file , compressed_gene_file, output_filename):

        # Load gene name to Ensembl id mappings
        self.get_gene_name2ensembl_mappings(compressed_gene_file)

        # Extract needed information from known target safety file
        self.build_json_safety(known_safety_file)

        # Extract needed information from experimental toxicity file
        self.build_json_experimental_toxicity(experimental_toxicity_file)

        # Write to tsv file
        safety_df = pd.DataFrame.from_dict(self.target_safety_info, orient='index', columns=['name', 'safety_risk', 'organs_systems_affected'])
        safety_df.index.name = "id"
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

    args = parser.parse_args()

    # Get parameters:
    known_safety_file = args.knownTargetSafetyFile
    experimental_toxicity_file = args.experimentalToxicityFile
    gene_file = args.geneFile
    output_file = args.output

    safety = Safety()
    safety.parse_safety(known_safety_file, experimental_toxicity_file, gene_file, output_file)


if __name__ == '__main__':
    main()
