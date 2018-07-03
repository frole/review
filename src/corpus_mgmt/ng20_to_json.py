""" This script loads the raw ng20 dataset and outputs a file containing a
    cleaned version of the datest with some metadata separate from the text.
"""
import sys; sys.path += ['../']
import json
import re
from constants import NG20_JSON_DS, NG5_JSON_DS
from sklearn.datasets import fetch_20newsgroups
from utils.regexes import *

ng5_categories = ['rec.motorcycles',
                  'rec.sport.baseball',
                  'comp.graphics',
                  'sci.space',
                  'talk.politics.mideast']

garbage_re = [PAT_URL,
              PAT_EMAIL,
              PAT_PHONE,
              PAT_BULLET_HYPHENS,
              PAT_GARBAGE,
              r'\ +']

for jsonfile, newsgroups in [(NG20_JSON_DS, fetch_20newsgroups(subset='all')),
                             (NG5_JSON_DS,
                              fetch_20newsgroups(subset='all',
                                                 categories=ng5_categories))]:
    with open(jsonfile, 'w') as fout:
        for document, label in zip(newsgroups.data, newsgroups.target):
            # the metadata header is delimited by a double newline character
            metadata_str, _, raw_text_str = document.partition('\n\n')

            metadata = metadata_str.split('\n')
            # in the metadata, each line of text is an entry of the form
            #       entryname: content
            # the first ':' is the delimiter between entry name and content
            metadata = {fragments[0]: fragments[2].strip() for fragments in
                        [entry.partition(':') for entry in metadata]}

            raw_text_str = raw_text_str.replace('\n', ' ')
            raw_text_str = raw_text_str.replace('\ti', ' ')
            raw_text_str = raw_text_str.replace('\t', ' ')
            for regex in garbage_re:
                raw_text_str = re.sub(regex, ' ', raw_text_str)

            article_dict = {"raw": raw_text_str,
                            "label": newsgroups.target_names[label]}
            for out_key, in_key in [("ab", 'Summary'),
                                    ("title", 'Subject'),
                                    ("kwds", 'Keywords')]:
                try:
                    article_dict[out_key] = metadata[in_key]
                except KeyError:
                    # case where a field didn't exist in the metadata
                    # typically "summary" and "Keywords"
                    article_dict[out_key] = ''

            json.dump(article_dict, fout)
            print('', file=fout)
