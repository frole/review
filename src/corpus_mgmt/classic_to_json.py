"""This module creates 2 JSON files containing the classic3 and classic4 datasets repectively"""
import sys; sys.path += ['../']
from constants import *
import os
import re
import json


def corpus_to_json(outfilename, datadir):
    labels = ["cisi", "cran", "med", "cacm"]

    with open(outfilename, 'w') as outfile:
        for filename in os.listdir(datadir):
            doc_label = ""
            for label in labels:
                if filename.find(label) == 0:  # if the filename starts with the label
                    doc_label = label
                    break  # not necessary to continue checking
            with open(datadir + filename) as f:
                raw_text = re.sub(" +", " ", " ".join([line for line in f]).replace('\n', ' ')).strip()

            json_dict = {"raw": raw_text, "label": doc_label}
            json.dump(json_dict, outfile)
            print('', file=outfile)


if __name__ == '__main__':
    corpus_to_json(CLASSIC3_JSON_DS, CLASSIC3_TXT_DIR)
    corpus_to_json(CLASSIC4_JSON_DS, CLASSIC4_TXT_DIR)
