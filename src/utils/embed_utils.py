""" This module contains utility functions for word or document
    embeddings that may be used accross multiple scripts
"""
import sys; sys.path += ['../']


def create_word_embeddings(corpusname,
                           save_to_file=False,
                           size=300,
                           window=5,
                           min_count=10,
                           workers=3):
    """ Creates word embeddings for a given corpus with gensim word2vec.
        Arguments:
        - (str) corpusname: name of the corpus to create WE for
        - (bool) save_to_file: boolean indicating whether the word
                               embeddings should be saved to a file or not.
                               Defaults to False.
        - (int) size: number of dimensions of the word embeddings.
                      Defaults to 300.
        - (int) window: number of context words to use when building
                        embeddings. Defaults to 5.
        - (int) min_count: words that occur less then  `min_count` times
                           will be ignored and will not have a vector.
                           Defaults to 10.
        - (int) workers: number of threads to use for computing.
                         Defaults to 3.
    """
    from sentence_generator import Sentences
    from gensim.models.word2vec import Word2Vec
    from misc_utils import get_json_dataset_by_name, get_w2v_model_by_name
    # creating word2vec model for the corpus with 300 dimensions, 5-grams,
    # ignoring words that occur less than 10 times and working on 3 cores
    # (4 would make the system unresponsive for 4-core systems)
    model = Word2Vec(Sentences(get_json_dataset_by_name(corpusname)),
                     size=size, window=window,
                     min_count=min_count, workers=workers)
    if save_to_file:
        model.save(get_w2v_model_by_name(corpusname))
    return model


def json_to_tagged_docs(json_doc):
    import re
    import string
    from gensim.models.doc2vec import TaggedDocument

    try:
        keywords = json_doc["kwds"].split(sep="+")
    except KeyError:
        keywords = []

    try:
        mesh = json_doc["mesh"].split(sep="+")
    except KeyError:
        mesh = []

    try:
        label = json_doc["label"]
    except KeyError:
        label = None
    tags = keywords + mesh + [label] if label is not None else keywords + mesh

    try:
        abstract = re.sub("[" + string.punctuation + "]", '',
                          json_doc["ab"].lower()).split()
    except KeyError:
        abstract = None

    if abstract is not None:
        abstract_tagged_doc = TaggedDocument(abstract, tags)
    else:
        abstract_tagged_doc = None

    fulltext = re.sub("[" + string.punctuation + "]", '',
                      json_doc["raw"].lower()).split()
    return abstract_tagged_doc, TaggedDocument(fulltext, tags)


def create_doc_embeddings(corpusnames):
    from gensim.models.doc2vec import Doc2Vec

    Doc2Vec(documents=None,
            dm_mean=None,
            dm=1,
            dbow_words=0,
            dm_concat=0,
            dm_tag_count=1,
            docvecs=None,
            docvecs_mapfile=None,
            comment=None,
            trim_rule=None,
            callbacks=())
    return Doc2Vec().wv
