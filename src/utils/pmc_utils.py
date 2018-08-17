""" This module contains utility functions pertaining to PMC and
    Pubmed tasks that may be used accross multiple scripts
"""
import sys; sys.path += ['../']


def get_full_papers(xml_dir, search_query, email="pmcdownloader@yopmail.com"):
    """ This script downloads and writes to disk the full text articles from
        PubMed Central returned by a query passed as argument.
        Arguments :
            - (str) xml_dir : path to the directory in which files should be downloaded
            - (str) search_query : a valid PMC search query
            - (str) email : an e-mail address at which to send E-utilities warnings
                            defaults to the public e-mail `pmcdownloader@yopmail.com`
    """
    from Bio import Entrez

    Entrez.email = email  # e-mail for problem reports

    errorfile = open("get_full_papers_error.txt", "w")

    # getting search results for the query
    search_results = Entrez.read(Entrez.esearch(db="pmc",
                                                term=search_query,
                                                retmax=10,
                                                usehistory="y"))

    # checking number of results found
    count = int(search_results["Count"])
    print("Found %i results" % count)

    batch_size = 1
    for start in range(1, count, batch_size):
        try:
            # getting a handle on the articles
            # we're going to have to use retmode="xml"
            # and parse the XML if we want full text
            handle = Entrez.efetch(db="pmc",
                                   rettype="full",
                                   retmode="xml",
                                   retstart=start,
                                   retmax=batch_size,
                                   webenv=search_results["WebEnv"],
                                   query_key=search_results["QueryKey"])

            full_xml = handle.read()
            with open(xml_dir + str(start) + ".xml", 'w') as xmlfile:
                print(full_xml, file=xmlfile)

        except Exception as e:
            print(e, file=errorfile)
            print("There was an error. See dump file for details")
            continue
            # sys.exit()
        handle.close()
    errorfile.close()


def get_mesh_from_PMID(pmid):
    """ Given a Pubmed ID as argument, returns a list of MeSH terms.
        If `pmid` is None or the empty string, returns an empty list rather
        than an error in order to facilitate automated batch calls.
        May take a long time to run as it has to download XML files from Pubmed.
    """
    from Bio import Entrez
    from xml.etree import ElementTree as ET
    from utils.json_xml_utils import flatten
    if pmid is None or pmid == "":
        return []
    try:
        handle = Entrez.efetch(db="pubmed",
                               id=pmid,
                               rettype="full",
                               retmode="xml")
    except Exception:
        return []
    full_xml = handle.read()
    tree = ET.fromstring(full_xml)
    meshtags = tree.findall(".//MeshHeadingList/MeshHeading/*")
    return [flatten(mesh) for mesh in meshtags]
