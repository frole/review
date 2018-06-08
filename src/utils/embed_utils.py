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
    from utils.misc_utils import get_json_dataset_by_name, get_w2v_model_by_name
    # creating word2vec model for the corpus with 300 dimensions, 5-grams,
    # ignoring words that occur less than 10 times and working on 3 cores
    # (4 would make the system unresponsive for 4-core systems)
    model = Word2Vec(Sentences(get_json_dataset_by_name(corpusname)),
                     size=size, window=window,
                     min_count=min_count, workers=workers)
    if save_to_file:
        model.save(get_w2v_model_by_name(corpusname))
    return model


def _json_to_tagged_docs(json_doc, tags):
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
        abstract = re.sub("[" + string.punctuation + "]", '',
                          json_doc["ab"].lower()).split()
    except KeyError:
        abstract = None

    if abstract is not None:
        abs_tags = ["+".join(tags + ['abstract'])]
        abstract_tagged_doc = TaggedDocument(abstract, abs_tags)
    else:
        abstract_tagged_doc = None

    fulltext = re.sub("[" + string.punctuation + "]", '',
                      json_doc["raw"].lower()).split()
    return abstract_tagged_doc, TaggedDocument(fulltext, ["+".join(tags)])


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
    from utils.misc_utils import get_docs_from_json_corpus
    docnumber = 0
    for doc in get_docs_from_json_corpus(corpusname=corpusname):
        tags = [corpusname, str(docnumber)]
        doc1, doc2 = _json_to_tagged_docs(doc, tags)
        docnumber += 1
        if doc1 is not None:
            yield doc1
        yield doc2


def corpora_to_tagged_docs(corporanames):
    """ Calls corpus_to_tagged_docs for multiple corpora
        Arguments:
            - (list<str>) corporanames: names of the corpora to tag
        Yields:
            for each document in each corpus:
            - (TaggedDocument): TaggedDocument for the abstract
                (if it is not None)
            - (TaggedDocument): TaggedDocument for the body of the article
    """
    # corporanames should be sorted in order for the tags to be sorted
    # in order for doctag_2_index to work
    for corpusname in sorted(corporanames):
        for tagged_doc in corpus_to_tagged_docs(corpusname):
            yield tagged_doc


def get_doc_from_tag(tag):
    """ From a tag returns the full text of the corresponding
        document according to the convention:
            tag = "corpusname+linenumber" for a normal text
            tag = "corpusname+linenumber+abstract" for an abstract
        Arguments:
            - (str) tag: a tag following the aforementioned convention
    """
    from utils.misc_utils import get_docs_from_json_corpus
    current_doc = 0
    tag = tag.split("+")
    for doc in get_docs_from_json_corpus(corpusname=tag[0]):
        # if the doc at current line is not equal to linenumber
        if current_doc != int(tag[1]):
            current_doc += 1
        elif 'abstract' in tag:
            return doc['ab']
        else:
            return doc['raw']


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
    model = Doc2Vec(documents=None,
                    dm=dm,
                    dbow_words=dbow_words,
                    dm_concat=dm_concat,
                    dm_tag_count=dm_tag_count,
                    trim_rule=trim_rule)
    train_corpus = corpora_to_tagged_docs(corporanames)
    model.build_vocab(train_corpus)
    model.train(train_corpus,
                total_examples=model.corpus_count,
                epochs=model.epochs)
    return model


def kv_index_to_doctag(keyedvectors, i_index):
    """ This function reimplements keyedvectors.index_to_doctag because the
        original implementation contains a bug (which has been fixed in later
        versions of gensim but which I can't use)
        Original docstring :
            Return string key for given i_index, if available. Otherwise
            return raw int doctag (same int).
    """
    candidate_offset = i_index - keyedvectors.max_rawint - 1
    if 0 <= candidate_offset < len(keyedvectors.offset2doctag):
        return keyedvectors.offset2doctag[candidate_offset]
    else:
        return i_index


def kv_indices_to_doctags(keyedvectors, indexlist):
    """ Equivalent to kv_index_to_doctag but takes a list of indices as arg
        and returns a generator on doctags
    """
    for i in indexlist:
        yield kv_index_to_doctag(keyedvectors, i)


def doctag2index(model, tag):
    """ Returns the index of the vector of the document of the specified tag
        for the specified model. Assumes the tags are comparable and were
        created in ascending order to achieve O(log(n)) complexity.
        Arguments:
            - (gensim.models.doc2vec.Doc2Vec) model: The relevant doc2vec
                model
            - (str) tag: the tag whose index is needed
        Returns:
            The index of the document corresponding to the specified tag
    """
    taglist = model.docvecs.index2entity
    # I know taglist is sorted so a dichotomy search will be more effective
    # than using the usual index() method.
    from utils.misc_utils import dichotomy
    return dichotomy(taglist, tag)
