"""This script downloads the full text medline articles about asthma from PubMed Central."""
import sys; sys.path += ['../']
from constants import EMAIL, LEUKEMIA_XML_DIR
from util.misc_utils import get_full_papers


# search query for open access medline articles about asthma
search_query = '("leukemia"[MeSH Terms] OR "leukemia"[All Fields]) AND ("open access"[filter] AND medline[sb])'

get_full_papers(email=EMAIL, xml_dir=LEUKEMIA_XML_DIR, search_query=search_query)
