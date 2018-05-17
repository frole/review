"""This script loads XML PMC articles and outputs a file containing stripped down JSON representations of the articles."""
import sys; sys.path += ['../']
from utils.json_xml_utils import xml_to_json
from constants import LEUKEMIA_JSON_DIR, LEUKEMIA_XML_DIR, LEUKEMIA_JSON_DS, EMAIL
from Bio import Entrez

if __name__ == '__main__':
    Entrez.email = EMAIL
    xml_to_json(json_dir=LEUKEMIA_JSON_DIR,
                xml_dir=LEUKEMIA_XML_DIR,
                json_dataset=LEUKEMIA_JSON_DS,
                label="leukemia")
