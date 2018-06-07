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
    """
    for corpusname in corporanames:
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


def get_topic_vecs(model, n_topics=20):
    """ Computes and returns the topic vectors of a doc2vec model. the topic
        vectors are simply the centroids of the classes after the documents
        have been clustered. They are therefore "virtual" documents that are
        an average of a group of similar documents.
        Arguments:
            - (gensim.models.doc2vec.Doc2Vec) model: A doc2vec model
            - (<float>) n_topics: The number of topics that should be
                found, defaults to 20.
        Returns:
            - (numpy.ndarray) topics: The topic vectors of the model
    """
    import numpy as np
    from sklearn.cluster import KMeans
    # making a numpy array from the data
    dv = np.array([model.docvecs[key] for key
                   in model.docvecs.doctags.keys()])
    # carrying out K-means to group documents by topic
    km_model = KMeans(n_clusters=n_topics, random_state=0).fit(dv)
    # extracting topic vectors (centroids of the groups)
    return km_model.cluster_centers_


def get_topic_word_prob(model):
    """ Computes and returns the probability for each word in the model's
        vocabulary to be generated by the underlying topics in the model
        Arguments:
            - (gensim.models.doc2vec.Doc2Vec) model: A doc2vec model
        Returns:
            - (list<ndarray, list<float, str>>) topic_word_probabilities:
                a list of tuples of the form:
                (topic, word_probabilities)
                    with word_probabilities a list of tuples of the form:
                    (probability, word)
    """
    import math
    topics = get_topic_vecs(model)

    class ProbDenom:
        """ This class is defined solely to allow for persistance of the
            denominator in `prob` function so that it is not re-computed
            every time the function is called
        """

        def __init__(self):
            self.topic = None
            self.value = None

        def compute(self, topic):
            """ Returns (computing only if not done previously) the
                denominator for the `prob` function given a certain topic.
                Arguments:
                    - (numpy.array) topic: the topic that would generate the
                        word `prob` is called for.
                Returns:
                    - The value of the denominator
            """
            if (topic != self.topic).any() or self.topic is None:
                self.topic = topic
                # model.wv.syn0: list of word vectors, access by index
                self.value = (sum([math.exp(wv.dot(topic))
                                   for wv in model.wv.syn0]))
            return self.value
    prob_denom = ProbDenom()

    def prob(word, topic_vec):
        """ Computes the probability of a word being generated by a topic
            (treating the topic as a document) given the word and the topic.
            Arguments:
                - (str) word: the word to be generated
                - (numpy.array) topic_vec: the topic that would generate `word`
            Returns:
                - P(word | topic_vec)
        """
        # I hope `S(W)`, the "weight vectors for calculating the word
        # prediction scores in the paragraph vector model" refers to
        # the word embeddings created by doc2vec

        # model.wv.word_vec(): accesses syn0 by word //=======
        # for the original formula see equation 5 in Hashimoto et al.'s
        # "Topic detection using paragraph vectors to support
        # active learning in systematic reviews", June 2016
        return (math.exp(model.wv.word_vec(word).dot(topic_vec)) /
                prob_denom.compute(topic_vec))

    # get top words from topic vectors
    #     get vocab
    vocab = set(model.wv.index2word)

    #     get probability for each topic to produce each word ; each topic
    #     is associated to a list that associates words and probabilities
    topic_word_probabilities = [
        # You may be wondering why my topics are named 'c'. Well, ask
        # Hashimoto, I'm just following the convention in the article.
        (c, [  # UNHASHABLE TYPE NDARRAY
            # this list contains tuples (prob, word).
            # Tuple comparison works as follows:
            # (a, b) < (c, d) <=> a < c or (a = c and b < d)
            # therefore, sorting this list will sort along probabilties
            # which allows us to easily get the top terms per topic
            (prob(w, c), w)
            for w in vocab
        ])  # one could use `.sorted` here rather than sort later but that is
        #    less memory-efficient as the list would need to be copied
        for c in topics
    ]
    for _, prob_word_list in topic_word_probabilities:
        # As mentioned earlier, we are sorting in order to get the top terms
        # per document and we're doing it after the fact as opposed to doing
        # it at the creation of the list because this is more efficient.
        prob_word_list.sort(reverse=True)
        del prob_word_list[5:]
    return topic_word_probabilities


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


def get_docs_in_topic_space(model, extra_doc=None):
    """ Computes and returns the document vectors expressed as a function
        of the topics.
        Arguments:
            - (gensim.models.doc2vec.Doc2Vec) model: A doc2vec model
            - (str) extra_doc: optional. If not None, will place the extra
                document in the topic space and return it
        Returns:
            - (np.matrix) docs: Matrix with all the document vectors
                expressed as a function of the topics.
            - (np.ndarray) extra_vec: the vector for the `extra_doc` in the
                topic space. If no `extra_doc` is given, will be None.
    """
    import math
    import numpy as np

    topics = get_topic_vecs(model)
    # modifying math.exp so that it can be applied over an array
    exp = np.vectorize(math.exp)
    # shortening function name
    m = np.matrix
    ndocs = len(model.docvecs)
    # projecting documents onto topics
    doc_topic_proj = model.docvecs.vectors_docs.dot(topics.T)

    # this is a vectorized version of equation 3 in Hashimoto et al.'s
    # "Topic detection using paragraph vectors to support
    # active learning in systematic reviews", June 2016
    # instead of computing each item independantly, we compute
    # the entire matrix at once
    docs_as_topics = (
        np.apply_along_axis(func1d=exp,
                            axis=0,
                            arr=doc_topic_proj) /
        m(np.ones(ndocs)).T.dot(m(exp(sum(doc_topic_proj))))
    )

    # This chunk of code is only for the case that we want to place an extra
    # document in the topic space
    new_vec_proj = None
    if extra_doc is not None:
        new_vector = model.infer_vector(extra_doc)
        # placing extra document in topic space
        new_vec_proj = (exp(new_vector.dot(topics.T)) /
                        (sum(exp(new_vector.dot(topics.T))) *
                         np.ones(len(topics))
                         )
                        )

    # here is a version that is vectorized to a lesser
    # degree (still looping on columns)
    # [exp(dv.dot(topics.T)) /
    #  (sum(exp(dv.dot(topics.T))) *
    #   np.ones(len(topics)))  # multiplying ones vector by a scalar returns a
    #                          # vector with many times the same value
    #  for dv in model.docvecs]

    return docs_as_topics, new_vec_proj
