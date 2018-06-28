"""This module creates a JSON file containing the reuters dataset"""
import sys; sys.path += ['../']
from constants import REUTERS_JSON_DS, REUTERS_TXT_FILE, REUTERS_LABELS
import re
import json


def get_labels():
    with open(REUTERS_LABELS) as labels:
        for label in labels:
            # strip() is necessary or else the labels
            # contain a newline character
            yield label.strip()


def corpus_to_json(outfilename, infilename):
    labels = get_labels()

    with open(outfilename, 'w') as outfile:
        with open(infilename, 'r') as infile:
            for doc in infile:
                doc_label = next(labels)
                raw_text = re.sub(" +", " ", doc).strip()

                json_dict = {"raw": raw_text, "label": doc_label}
                json.dump(json_dict, outfile)
                print('', file=outfile)


if __name__ == '__main__':
    corpus_to_json(REUTERS_JSON_DS, REUTERS_TXT_FILE)
