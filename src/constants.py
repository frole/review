"""This module contains the constants (such as paths) shared by multiple scripts"""
import os
cwd = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = cwd + "/../data/"

EMAIL = "guilhem.piat@etu.parisdescartes.fr"
KNOWN_DATASETS = ["asthma", "autism", "leukemia", "classic3", "classic4",
                  "20newsgroups", "ng5", "test1", "test2"]


# Asthma
ASTHMA_DATA_DIR = DATA_DIR + "asthma/"
ASTHMA_XML_DIR = ASTHMA_DATA_DIR + "xml/"
ASTHMA_JSON_DIR = ASTHMA_DATA_DIR + "json/"
ASTHMA_DIR = cwd + "/asthma/"

ASTHMA_JSON_DS = ASTHMA_JSON_DIR + "pmc_asthma.json"  # file conatining the dataset as JSON

ASTHMA_PMID_FILE = ASTHMA_DIR + "ids.txt"  # file containing PMIDs of articles
ASTHMA_MESH_PKL = ASTHMA_DIR + "asthma_meshterms.pkl"  # file containing pickled mesh terms
NON_ASTHMA_MESH_PKL = ASTHMA_DIR + "non_asthma_meshterms.pkl"  # file containing pickled mesh terms


# Autism
AUTISM_DATA_DIR = DATA_DIR + "autism/"
AUTISM_XML_DIR = AUTISM_DATA_DIR + "xml/"
AUTISM_JSON_DIR = AUTISM_DATA_DIR + "json/"

AUTISM_JSON_DS = AUTISM_JSON_DIR + "pmc_autism.json"


# Leukemia
LEUKEMIA_DATA_DIR = DATA_DIR + "leukemia/"
LEUKEMIA_XML_DIR = LEUKEMIA_DATA_DIR + "xml/"
LEUKEMIA_JSON_DIR = LEUKEMIA_DATA_DIR + "json/"

LEUKEMIA_JSON_DS = LEUKEMIA_JSON_DIR + "pmc_leukemia.json"


# Classic
CLASSIC_DIR = cwd + "/classic/"

CLASSIC3_DATA_DIR = DATA_DIR + "classic3/"
CLASSIC3_TXT_DIR = CLASSIC3_DATA_DIR + "text/"
CLASSIC3_JSON_DIR = CLASSIC3_DATA_DIR + "json/"
CLASSIC3_JSON_DS = CLASSIC3_JSON_DIR + "classic3.json"  # file conatining the dataset as JSON

CLASSIC4_DATA_DIR = DATA_DIR + "classic4/"
CLASSIC4_TXT_DIR = CLASSIC4_DATA_DIR + "text/"
CLASSIC4_JSON_DIR = CLASSIC4_DATA_DIR + "json/"
CLASSIC4_JSON_DS = CLASSIC4_JSON_DIR + "classic4.json"  # file conatining the dataset as JSON

# TEST
TEST_DATA_DIR = DATA_DIR + "test/"
TEST1_JSON_DS = TEST_DATA_DIR + "test1.json"
TEST2_JSON_DS = TEST_DATA_DIR + "test2.json"

# TEMP
RESULT_DIR = DATA_DIR + "results/"

# MODELS
MODEL_DIR = DATA_DIR + "models/"
GLOVE = MODEL_DIR + "glove.840B.300d_as_w2v.txt"
GOOGLE_NEWS = MODEL_DIR + "GoogleNews-vectors-negative300.bin"
AUTISM_W2V_PKL = MODEL_DIR + "autism_model.w2v"
LEUKEMIA_W2V_PKL = MODEL_DIR + "leukemia_model.w2v"
CLASSIC3_W2V_PKL = MODEL_DIR + "classic3_model.w2v"
CLASSIC4_W2V_PKL = MODEL_DIR + "classic4_model.w2v"
_W2V_PKL = MODEL_DIR + "_model.w2v"

# WEB
PLOT_DIR = "/static/plots/"
WEBAPP_DIR = cwd + "/webapp/"
TOP_TERMS_PLT = PLOT_DIR + "top_terms.png"
CLSTR_SIZE_PLT = PLOT_DIR + "cluster_sizes.png"
REORG_MATRIX_PLT = PLOT_DIR + "reorganized_matrix.png"
PLOT_FILES_READ = [TOP_TERMS_PLT, CLSTR_SIZE_PLT, REORG_MATRIX_PLT]
PLOT_FILES_WRITE = [WEBAPP_DIR + plot for plot in PLOT_FILES_READ]

# Open Targets
TAG_CATEGORIES = ['ORGANISM', 'DISEASE', 'DISEASEALT', 'GENE', 'DRUG', 'ANATOMY', 'LOC', 'PHENOTYPE', 'HEALTHCARE', 'PROCESS', 'DIAGNOSTICS']
