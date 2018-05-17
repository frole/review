"""This script downloads the full text medline articles about asthma from PubMed Central."""
import sys; sys.path += ['../']
from constants import EMAIL, AUTISM_XML_DIR
from util import get_full_papers


# search query for open access medline articles about asthma
search_query = '("autism"[MeSH Terms] OR "autism"[All Fields]) AND ("open access"[filter] AND medline[sb])'

get_full_papers(email=EMAIL, xml_dir=AUTISM_XML_DIR, search_query=search_query)
