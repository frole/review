"""This script loads XML PMC articles and outputs a file containing stripped down JSON representations of the articles."""
import sys; sys.path += ['../']
from util import xml_to_json
from constants import AUTISM_JSON_DIR, AUTISM_XML_DIR, AUTISM_JSON_DS, EMAIL
from Bio import Entrez

if __name__ == '__main__':
    Entrez.email = EMAIL
    xml_to_json(json_dir=AUTISM_JSON_DIR,
                xml_dir=AUTISM_XML_DIR,
                json_dataset=AUTISM_JSON_DS,
                label="autism")
