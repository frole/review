import sys; sys.path += ['../']
from NER.BioentityTagger import BioEntityTagger
from constants import ASTHMA_JSON_DS
import json

bet = BioEntityTagger()
tag_whitelist = ['ORGANISM', 'DISEASE', 'DISEASEALT', 'GENE', 'DRUG', 'ANATOMY', 'LOC']
tag_blacklist = ['PHENOTYPE', 'HEALTHCARE', 'PROCESS', 'DIAGNOSTICS']

with open(ASTHMA_JSON_DS) as f:
    for line in f:
        article = json.loads(line)
        tags = [tag for tag in bet.tag(article["raw"]) if tag['category'] not in tag_blacklist]
        break

i = 0
while i < len(tags):
    # finding all the items that start at the same index as some other
    ends_of_tags_that_start_at_same_index = \
        [tag['end'] for tag in tags if tag['start'] == tags[i]['start']]
    # deleting the current tag if it ends after another tag that starts at the same index
    # this means deleting tags that contain others
    if tags[i]['end'] > min(ends_of_tags_that_start_at_same_index):
        del tags[i]


tags[0].keys()

# if tag['category'] not in tag_blacklist
