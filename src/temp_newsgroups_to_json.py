# trying to parse ng20
import re
from sklearn.datasets import fetch_20newsgroups
from utils.regexes import *

newsgroups = fetch_20newsgroups(subset='all')
garbage_re = [PAT_URL,
              PAT_EMAIL,
              PAT_PHONE,
              PAT_BULLET_HYPHENS,
              PAT_GARBAGE,
              '\\ +']

for document in newsgroups.data:
    # the metadata header is delimited by a double newline character
    metadata_str, _, raw_text_str = document.partition('\n\n')

    metadata = metadata_str.split('\n')
    # in the metadata, each line of text is an entry of the form
    #       entryname: content
    # the first ':' is the delimiter between entry name and content
    metadata = {fragments[0]: fragments[2].strip() for fragments in
                [entry.partition(':') for entry in metadata]}

    raw_text_str = raw_text_str.replace('\n', ' ')
    for regex in garbage_re:
        raw_text_str = re.sub(regex, ' ', raw_text_str)
        print(raw_text_str)
        input()


# metadata = [ls for ls in preprocessed if ':' in ls]
# fulltext = [ls for ls in preprocessed if ':' not in ls and ls != '']


article_dict = {
    "ab": metadata_d['Summary'],
    "title": metadata_d['Subject'],
    "kwds": metadata_d['Keywords'],
    "raw": raw_text_str
}
"""
o = {"ab": abs_text, "raw": body_text, "kwds": kwds,
                 "mesh": meshlist, "journ": journ, "title": title,
                 "pmid": pmid, "pmc": pmc, "label": label}
"""
