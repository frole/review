"""This script downloads the full text medline articles about rhinitis from PubMed Central."""
import sys; sys.path += ['../']
from constants import EMAIL, RHINITIS_XML_DIR
from utils.pmc_utils import get_full_papers


# search query for open access medline articles about rhinitis
search_query = '("rhinitis"[MeSH Terms] OR "rhinitis"[All Fields]) AND ("open access"[filter] AND medline[sb])'

get_full_papers(email=EMAIL, xml_dir=RHINITIS_XML_DIR, search_query=search_query)
