""" This module contains utility functions for topic management in
    document embeddings that may be used accross multiple scripts
"""
import sys; sys.path += ['../']


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
    from sklearn.cluster import KMeans
    # getting the data as a numpy array
    dv = model.docvecs.vectors_docs
    # carrying out K-means to group documents by topic
    km_model = KMeans(n_clusters=n_topics, random_state=0).fit(dv)
    # extracting topic vectors (centroids of the groups)
    return km_model.cluster_centers_


def get_topic_word_prob(model, cutoff=5):
    """ Computes and returns the probability for each word in the model's
        vocabulary to be generated by the underlying topics in the model
        Arguments:
            - (gensim.models.doc2vec.Doc2Vec) model: A doc2vec model
            - (int) cutoff: how many top words should be kept per topic.
                defaults to 5, if None or 0 will return all words
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

    # setting cutoff to return all words if cutoff is None or 0
    if cutoff is None or cutoff == 0:
        cutoff = len(vocab)

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
        del prob_word_list[cutoff:]
    return topic_word_probabilities


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


def get_doc_topic_sim(model=None,
                      docs_proj=None,
                      extra_doc_str=None,
                      xtra_doc_proj=None):
    """ This function returns the cosine similarity between a set of doc
        vectors and an extra document, all projected in the topic space
        Either `model` AND `extra_doc_str` should be passed XOR
        `docs_proj` AND `xtra_doc_proj` should be passed.
        Arguments:
            - (gensim.models.doc2vec.Doc2Vec) model: the document embeddings
                model.
            - (np.matrix) docs_proj: the document embeddings projected in the
                topic space as returned by get_docs_in_topic_space.
            - (str) extra_doc_str: the document to compare to the other
                documents in the model.
            - (numpy.ndarray) xtra_doc_proj: vector projected in the topic
                space corresponding to extra_doc_str, as returned by
                get_docs_in_topic_space.
        Returns:
            - (generator<str>) top_docs: doc tags of the docs most
                similar to extra_doc_str.
            - (list<float>) top_similarities: cosine similarity of the
                docs most similar to extra_doc_str.
    """
    import numpy as np
    from numpy import matrix as m
    from utils.embed_utils import get_docs_in_topic_space

    case1 = (model is not None and extra_doc_str is not None)
    case2 = (docs_proj is not None and xtra_doc_proj is not None)
    assert case1 or case2

    if case2:
        docs = docs_proj
        input_doc = xtra_doc_proj
    else:
        docs, input_doc = get_docs_in_topic_space(model, extra_doc=extra_doc_str)

    # we want the cosine similarity between each document and the input
    # document therefore, we want (u.v)/(|u|*|v|) for all u in docs and
    # v the input document
    # therefore, we want:
    #     - the dot product of all docs with input which should give us an
    #         ndocsx1 vector with all the dot products, which is (X.v^t)
    #         with X=docs, v the input doc, and ^t is transposition
    #     - the product of the norms of all the vectors, for which we will
    #       use np.linalg.norm, specifying the axis that yields an ndocsx1
    #       vector in the case of `docs`
    # for numpy vector representation reasons, we have to transpose one
    # side of the division
    doc_similarities = (docs.dot(m(input_doc).T) /
                        (np.linalg.norm(input_doc) *
                            m(np.linalg.norm(docs, axis=1))).T)
    return doc_similarities


def get_top_docs_by_topic_sim(n,
                              model=None,
                              docs_proj=None,
                              extra_doc_str=None,
                              xtra_doc_proj=None):
    """ This function fetches the cosine similarity between a set of doc
        vectors and an extra document, all projected in the topic space,
        and returns the top `n` similarities in decreasing order as well
        as the corresponding doc tags.
        Either `model` AND `extra_doc_str` should be passed XOR
        `docs_proj` AND `xtra_doc_proj` should be passed.
        Arguments:
            - (int) n: number of top documents to return
            - (gensim.models.doc2vec.Doc2Vec) model: the document embeddings
                model.
            - (np.matrix) docs_proj: the document embeddings projected in the
                topic space as returned by get_docs_in_topic_space.
            - (str) extra_doc_str: the document to compare to the other
                documents in the model.
            - (numpy.ndarray) xtra_doc_proj: vector projected in the topic
                space corresponding to extra_doc_str, as returned by
                get_docs_in_topic_space.
        Returns:
            - (generator<str>) top_docs: doc tags of the top n docs most
                similar to extra_doc_str.
            - (list<float>) top_similarities: cosine similarity of the top n
                docs most similar to extra_doc_str.
    """
    from utils.embed_utils import kv_indices_to_doctags
    import numpy as np
    doc_similarities = get_doc_topic_sim()
    # argsort yields the original indices of the values in the sorted array
    # [::-1] reverses the array
    # [:n] slices off the top n values
    top_indices = np.argsort(list(doc_similarities.flat))[::-1][:n]
    top_docs = kv_indices_to_doctags(model.docvecs, top_indices)
    top_similarities = [doc_similarities.flat[i] for i in top_indices]

    return top_docs, top_similarities


def get_flop_docs_by_topic_sim(n,
                               model=None,
                               docs_proj=None,
                               extra_doc_str=None,
                               xtra_doc_proj=None):
    """ This function is identical to `get_top_docs_by_topic_sim` but returns
        the n most different documents.
    """
    from utils.embed_utils import kv_indices_to_doctags
    import numpy as np
    doc_similarities = get_doc_topic_sim()
    # argsort yields the original indices of the values in the sorted array
    # [:n] slices off the n first values
    flop_indices = np.argsort(list(doc_similarities.flat))[:n]
    flop_docs = kv_indices_to_doctags(model.docvecs, flop_indices)
    flop_similarities = [doc_similarities.flat[i] for i in flop_indices]

    return flop_docs, flop_similarities


def get_top_and_flop_docs_top_sim(n,
                                  m,
                                  model=None,
                                  docs_proj=None,
                                  extra_doc_str=None,
                                  xtra_doc_proj=None):
    """ This function fuses `get_top_docs_by_topic_sim` and
        `get_flop_docs_by_topic_sim`. The `n` argument corresponds to the
        `n` argument of `get_top_docs_by_topic_sim` and the `m` argument
         corresponds to the `n` argument of `get_flop_docs_by_topic_sim`.
         Returns:
            top_docs
            flop_docs
        Performance-wise, this function is better than individual calls to
        get_top_docs_by_topic_sim and get_flop_docs_by_topic_sim.
    """
    from utils.embed_utils import kv_indices_to_doctags
    import numpy as np
    doc_similarities = get_doc_topic_sim()
    sim = np.argsort(list(doc_similarities.flat))
    flop_indices = sim[:m]
    top_indices = sim[::-1][:n]
    flop_docs = kv_indices_to_doctags(model.docvecs, flop_indices)
    top_docs = kv_indices_to_doctags(model.docvecs, top_indices)

    return top_docs, flop_docs
