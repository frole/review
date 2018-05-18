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


def _json_to_tagged_docs(json_doc):
    """ Turns a document loaded from a corpus into 2 TaggedDocuments
        Arguments:
            - (dict) json_doc: a document read with `json.loads` from a corpus
        Returns:
            - (TaggedDocument): TaggedDocument for the abstract
                (or None if there is none)
            - (TaggedDocument): TaggedDocument for the body of the article
    """
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


def corpus_to_tagged_docs(corpusname):
    """ Generator for TaggedDocuments from a corpus
        Arguments:
            - (str) corpusname : the name of the corpus to tag
        Yields:
            for each document in corpus:
            - (TaggedDocument): TaggedDocument for the abstract
                (if it is not None)
            - (TaggedDocument): TaggedDocument for the body of the article
    """
    from misc_utils import get_docs_from_json_corpus
    for doc in get_docs_from_json_corpus(corpusname=corpusname):
        doc1, doc2 = _json_to_tagged_docs(doc)
        if doc1 is not None:
            yield doc1
        yield doc2


def corpora_to_tagged_docs(corporanames):
    """ Calls corpus_to_tagged_docs for multiple corpora
    """
    for corpusname in corporanames:
        for tagged_doc in corpus_to_tagged_docs(corpusname):
            yield tagged_doc


def create_doc_embeddings(corporanames,
                          dm=1,
                          dbow_words=0,
                          dm_concat=0,
                          dm_tag_count=1,
                          trim_rule=None):
    """ Creates Document embeddings (paragraph vectors) for the specified corpora
        Arguments:
            - (list<str>) corporanames: a list of corpus names for which
                embeddings should be created
            - (int {1,0}) dm: Defines the training algorithm. If dm=1,
                'distributed memory' is used. Otherwise, distributed
                bag of words.
            - (int {1,0}) dbow_words:
                    1 - trains word-vectors (skip-gram)
                    0 - only trains doc-vectors (faster)
            - (int {1,0}) dm_concat:
                    1 - use concatenation of context vectors
                    0 - use sum/average of context vectors (smaller model)
            - (int) dm_tag_count: Expected constant number of document tags
                per document, when using dm_concat mode; default is 1.
            - (function) trim_rule: Vocabulary trimming rule. Can be None
                (min_count will be used), or a callable that accepts parameters
                (word, count, min_count) and returns gensim.utils.RULE_DISCARD,
                gensim.utils.RULE_KEEP or gensim.utils.RULE_DEFAULT (min_count
                will be used). The rule is not stored as part of the model.
    """
    from gensim.models.doc2vec import Doc2Vec
    model = Doc2Vec(documents=corpora_to_tagged_docs(corporanames),
                    dm=dm,
                    dbow_words=dbow_words,
                    dm_concat=dm_concat,
                    dm_tag_count=dm_tag_count,
                    trim_rule=trim_rule)
    return model
