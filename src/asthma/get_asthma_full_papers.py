"""This script downloads the full text medline articles about asthma from PubMed Central."""
import sys; sys.path += ['../']
from constants import EMAIL, ASTHMA_XML_DIR
from utils.misc_utils import get_full_papers

# search query for open access medline articles about asthma
search_query = '("asthma"[MeSH Terms] OR "asthma"[All Fields]) AND ("open access"[filter] AND medline[sb])'

get_full_papers(email=EMAIL, xml_dir=ASTHMA_XML_DIR, search_query=search_query)
