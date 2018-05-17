import sys; sys.path += ['../']
import random
import pickle
import os
from constants import ASTHMA_MESH_PKL, NON_ASTHMA_MESH_PKL

# loading a pickle of the MeSH found in the Asthma corpus
with open(ASTHMA_MESH_PKL, 'rb') as f:
    asthma_mesh = pickle.load(f)

asthma_mesh = set(asthma_mesh)  # removing duplicates

# getting all mesh terms (the full list is split into several XML files)
all_mesh = []
mesh_dir = "./MeSH_XML/"
for filename in os.listdir(mesh_dir):  # for each XML file containing MeSH
    with open(mesh_dir + filename) as f:
        # XML files are too heavy to parse as a tree
        # finding each line with a String tag, removing tags and adding to the list of MeSH
        all_mesh += [line.replace("<String>", '').replace("</String>", '').strip()
                     for line in f if line.find("<String>") != -1]
all_mesh = set(all_mesh)  # removing duplicates


non_asthma_mesh = all_mesh - asthma_mesh  # set substraction
# getting a random sample of non-asthma MeSH as large as the number of MeSH in the asthma corpus
sample = random.sample(non_asthma_mesh, len(asthma_mesh))

with open(NON_ASTHMA_MESH_PKL, 'wb') as f:
    pickle.dump(sample, f)
