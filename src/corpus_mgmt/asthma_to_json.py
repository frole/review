"""This script loads XML PMC articles and outputs a file containing stripped down JSON representations of the articles."""
import sys; sys.path += ['../']
from utils.json_xml_utils import xml_to_json
from constants import ASTHMA_JSON_DIR, ASTHMA_XML_DIR, ASTHMA_JSON_DS, EMAIL
from Bio import Entrez

if __name__ == '__main__':
    Entrez.email = EMAIL
    xml_to_json(json_dir=ASTHMA_JSON_DIR,
                xml_dir=ASTHMA_XML_DIR,
                json_dataset=ASTHMA_JSON_DS,
                label="asthma")
