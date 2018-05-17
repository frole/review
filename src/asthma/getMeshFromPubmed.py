"""This script opens a file containing a list of PMIDs, downloads the relevant pubmed articles and extracts the MeSH terms."""
import sys; sys.path += ['../']
import pickle
from Bio import Entrez
import json
from constants import ASTHMA_PMID_FILE, ASTHMA_JSON_DS, ASTHMA_MESH_PKL, EMAIL
from utils.misc_util import file_len, get_mesh_from_PMID

Entrez.email = EMAIL  # e-mail for problem reports

if __name__ == '__main__':
    with open(ASTHMA_PMID_FILE, 'w') as idfile:
        with open(ASTHMA_JSON_DS) as file:
            for line in file:
                article = json.loads(line)
                pmid = article["pmid"]
                if pmid is not None and pmid != "":
                    print(pmid, file=idfile)

    meshlist = []
    with open(ASTHMA_PMID_FILE) as idfile:
        for i in range(1, file_len(ASTHMA_PMID_FILE)):
            meshlist += get_mesh_from_PMID(pmid)

    with open(ASTHMA_MESH_PKL, 'wb') as f:
        pickle.dump(meshlist, f)
