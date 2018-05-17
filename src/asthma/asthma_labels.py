import sys; sys.path += ['../']
import json
from constants import ASTHMA_JSON_DS


asthma, leukemia, cardiac, autism, n = 0, 0, 0, 0, 0
with open(ASTHMA_JSON_DS) as f:
    for line in f:
        article = json.loads(line)
        try:
            if article['title'].lower().find('asthma') != -1:
                asthma += 1
            if article['title'].lower().find('cardiac') != -1:
                cardiac += 1
            if article['title'].lower().find('leukemia') != -1:
                leukemia += 1
            if article['title'].lower().find('autism') != -1:
                autism += 1
        except AttributeError:
            n += 1
print(asthma, leukemia, cardiac, autism, n)
input()
# title contains asthma : 3033
# title contains leukemia : 60
# title contains cardiac : 218
# title contains autism : 105
# no title : 420

# asthma, leukemia, autism
