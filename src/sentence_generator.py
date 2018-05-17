"""This module defines a data structure that can be lazily iterated on multiple times to provide articles as lists of sentences"""
import sys; sys.path += ['../']
import json
import re
import string


class Sentences():  # generator on the text in the corpus
    def __init__(self, filename):
        self.filename = filename

    def __iter__(self):
        return next(self)

    def __next__(self):
        # regex containing all punctution
        punct_regex = '[' + string.punctuation + ']'
        with open(self.filename) as corpus:
            for article_as_json in corpus:
                # loading each json article
                article = json.loads(article_as_json)
                # removing punctuation, converting to lower case,
                # removing article separators, loading each line
                # as a seperate document
                try:
                    # yielding abstract
                    yield re.sub(punct_regex, '', article["ab"].lower()).split()
                except KeyError:  # ignore if article has no abstract
                    pass
                # yielding full article text
                yield re.sub(punct_regex, '', article["raw"].lower()).split()
