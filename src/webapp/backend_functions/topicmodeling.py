import sys; sys.path += ['../../']  # used to import modules from grandparent directory
import random

from flask import request, session, redirect
from utils.web_utils import build_page, corpus_selector, TEST_STRING, make_submit_group, make_btn_group, create_doc_display_areas
from utils.embed_utils import create_doc_embeddings

doc_vec_model = create_doc_embeddings(corporanames=["test1"])


def topic_modeling():
    """ Returns the webpage at <host URL>/biomed/topicmodeling
    """
    if request.method == 'GET':
        selector = corpus_selector(classes=["topic-form"], form_id="topic-form")
        # selector for the algorithm DM vs. DBOW (dm argument for doc2vec)
        separator = ['<div style="width:100%;height:15px;"></div>']
        algorithm = ['<label>Algorithm:',
                     '<select name="dm" form="topic-form">',
                     '<option value="1">Distributed Memory</option>',
                     '<option value="0">Distributed Bag of Words</option>',
                     '</select>',
                     '</label>']
        # checkbox for whether or not to train word vectors (dbow_words)
        train_wv = ['<label><input type="checkbox" form="topic-form" name="dbow_words"/> Train word vectors?</label>']
        context_representation = ['<label>Context vector representation:',
                                  '<select name="dm_concat" form="topic-form">',
                                  '<option value="0">Sum / average (faster)</option>',
                                  '<option value="1">Concatenation</option>',
                                  '</select>',
                                  '</label>']
        options = (['<div class="checkbox-form">', ''] +
                   algorithm + separator +
                   train_wv + separator +
                   context_representation + ['</div>'])
        return build_page(title="Topic Modeling",
                          contents=selector,
                          sidebar=options,
                          backtarget="/biomed")

    else:
        global doc_vec_model

        # getting all form elements to send as arguments to doc2vec
        corpus = request.form['corpus']
        # saving corpus in session for later
        session['corpora'] = [corpus]
        dm = int(request.form['dm'])
        dbow_words = 0
        if ('dbow_words' in request.form and
                request.form['dbow_words'] == 'on'):
            dbow_words = 1
        dm_concat = int(request.form['dm_concat'])

        # creating doc2vec model
        doc_vec_model = create_doc_embeddings(corporanames=[corpus],
                                              dm=dm,
                                              dbow_words=dbow_words,
                                              dm_concat=dm_concat)
        # redirecting with code 307 to ensure redirect uses POST
        return redirect('/biomed/topicmodeling/topics', code=307)


def topic_modeling_top_words():
    import math
    import numpy as np
    from utils.misc_utils import get_vocab
    from sklearn.cluster import KMeans

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
            if topic != self.topic:
                self.topic = topic
                # doc_vec_model.wv.syn0: list of word vectors, access by index
                self.value = (sum([math.exp(wv.dot(topic))
                                   for wv in doc_vec_model.wv.syn0]))
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

        # doc_vec_model.wv.word_vec(): accesses syn0 by word //=======
        # for the original formula see equation 5 in Hashimoto et al.'s
        # "Topic detection using paragraph vectors to support
        # active learning in systematic reviews", June 2016
        return (math.exp(doc_vec_model.wv.word_vec(word).dot(topic_vec)) /
                prob_denom.compute(topic_vec))

    # making a numpy array from the data
    dv = np.array([doc_vec_model.docvecs[key] for key
                   in doc_vec_model.docvecs.doctags.keys()])
    # carrying out K-means to group documents by topic
    km_model = KMeans(n_clusters=20, random_state=0).fit(dv)
    # extracting topic vectors (centroids of the groups)
    topics = km_model.cluster_centers_

    # get top words from topic vectors
    #     get vocab
    vocab = set(doc_vec_model.wv.index2word)

    #     get probability for each topic to produce each word ; each topic
    #     is associated to a list that associates words and probabilities
    topic_word_probability = {
        # You may be wondering why my topics are named 'c'. Well, ask
        # Hashimoto, I'm just following the convention in the article.
        c: [
            # this list contains tuples (prob, word).
            # Tuple comparison works as follows:
            # (a, b) < (c, d) <=> a < c or (a = c and b < d)
            # therefore, sorting this list will sort along probabilties
            # which allows us to easily get the top terms per topic
            (prob(w, c), w)
            for w in vocab
        ]  # one could use `.sorted` here rather than sort later but that is
        #    less memory-efficient as the list would need to be copied
        for c in topics
    }
    for _, prob_word_list in topic_word_probability.items():
        # As mentioned earlier, we are sorting in order to get the top terms
        # per document and we're doing it after the fact as opposed to doing
        # it at the creation of the list because this is more efficient.
        prob_word_list.sort(reverse=True)
        del prob_word_list[5:]

    # creating the dict to send to create_doc_display_areas
    # Keys will be headers for "documents", so the keys will be "Topic 1" etc.
    # Values are "documents", or strings that should be displayed
    # we want to display something of the form:
    #     Aardvark: 89%
    #     Bumblebee: 80%
    # etc. We get topics, words and percentages from `topic_word_probability`,
    # and format words and percentages with a `join`ed list comprehension
    # and get the number of the topic by simultaneously iterating over
    # `range(len(topic_word_probability))` thanks to `zip()`.
    topic_top_terms = {("Topic " + str(i) + ": "):
                       '\n'.join([word + ": " + str(int(prob * 100)) + "%"
                                  for prob, word in pw_list])
                       for i, (_, pw_list) in
                       zip(range(len(topic_word_probability)),
                           topic_word_probability.items())}

    contents = create_doc_display_areas(documents=topic_top_terms)\
        + make_btn_group(labels=["Proceed"],
                         targets=["/biomed/topicmodeling/use"])

    # express documents as a function of topics
    # {tag: dv[tag] for tag in dv.doctags.keys()}

    return build_page(title="Top words per topic",
                      contents=contents)


def topic_modeling_active_learning():
    from utils.embed_utils import get_doc_from_tag
    from utils.web_utils import create_doc_display_areas, create_radio_group

    # placeholder : Further down the line, this method should be an
    # interface for active learning. Maybe make a page specifically
    # for the doc embeddings and then one to access previously
    # created embeddings in order to redirect the user to something
    # else while the computing is happening.
    if "proceed" in request.form:
        # redirecting with code 307 to ensure redirect uses POST
        return redirect('/biomed/topicmodeling/use/docsim', code=307)

    # `doc_vec_model.docvecs.doctags` is a dict such that each entry is of the
    # form `tag: document_descriptor` where `tag` is a document identifier
    # (a "tag" for a TaggedDoc) and `document_descriptor` is a `Doctag` which
    # aggregates some metadata on the corresponding document. Getting the keys
    # of this dict returns a `dict_keys` object of all the tags in the model.
    # This object is not subscriptable but can be coerced to a list. //======
    # Of this list of tags, we are selecting 5 randomly as a placeholder
    # until the active learning is actually implemented.
    doc_tags = random.sample(
        population=list(doc_vec_model.docvecs.doctags.keys()),
        k=5)

    # getting documents from tags and putting in a dict
    # for `create_doc_display_areas`
    docs = {"Corpus: " + tag.split('+')[0] + ", Doc #" + tag.split('+')[1]:
            (get_doc_from_tag(tag),
                create_radio_group(name="radio-" + tag,
                                   labels=["Relevant", "Irrelevant"],
                                   values=["relevant", "irrelevant"],
                                   checked="relevant",
                                   form_id="active-form")
             )
            for tag in doc_tags}

    # transforming into display areas
    doc_display_areas = create_doc_display_areas(documents=docs)
    # the contents of the webpage are the documents in their display areas
    # each followed by the radio buttons for each document
    contents = doc_display_areas
    contents += ['<form method="POST" class="" id="active-form">']
    contents += make_submit_group(labels=["Submit", "Submit & Proceed"],
                                  names=["submit", "proceed"])
    contents += ['</form>']

    sidebar = ['<p>',
               'Topic 1: <br />',
               'Topic 2: <br />',
               'Topic 3: <br />',
               'Topic 4: <br />',
               'Topic 5: <br />',
               '</p>']

    return build_page(title="Topic Modeling",
                      contents=contents,
                      sidebar=sidebar,
                      backtarget="/biomed/topicmodeling")


def topic_modeling_use():
    if "back" in request.form or "proceed" in request.form or request.method == 'GET':
        # content is a textarea in which one enters the text to infer
        content = ['<form method="POST" class="text-area-form" id="text-area-form">'
                   '<textarea name="text" rows="10" cols="75">',
                   TEST_STRING,
                   '</textarea>', '<br/>',
                   '<br /> Or drag & drop a file <br />',
                   '<label>Or enter a document tag: <input type="text" name="doc_tag" form="text-area-form" size="20"/></label>',
                   '</form>']

        content += make_submit_group(labels=["Search by document similarity",
                                             "Search by topic similarity",
                                             "Classify documents by relevancy"],
                                     names=["doc_sim",
                                            "topic_sim",
                                            "active"],
                                     form_id="text-area-form")
    # options allow users to select the number of documents they want
        options = ['<label>Number of documents to retrieve: <input type="text" name="topn" form="text-area-form" value="3" size="2"/></label>']
        return build_page(title="Topic Modeling",
                          contents=content,
                          sidebar=options,
                          backtarget="/biomed/topicmodeling/topics")

    # Code only reachable if POST request not from "back" (i.e. not from
    # document list) and not from "proceed" (i.e. not from active learning)
    # therefore only reachable if coming from /biomed/topicmodeling/use textarea form
    else:
        from utils.embed_utils import get_doc_from_tag
        # saving form to session
        # getting new document : priority #1 is D&D (NYI)
        #                                 #2 is doc_tag
        #                                 #3 is entered text
        if "doc_tag" in request.form and request.form["doc_tag"] != '':
            new_doc = get_doc_from_tag(request.form["doc_tag"])
        else:
            new_doc = request.form["text"].split()
        session['document'] = new_doc
        session['topn'] = request.form["topn"]

        if "doc_sim" in request.form:  # 1st submit button
            return redirect('/biomed/topicmodeling/use/docsim', code=307)
        elif "topic_sim" in request.form:  # 2nd submit button
            return redirect('/biomed/topicmodeling/use/topicsim', code=307)
        else:  # 3rd submit button
            return redirect('/biomed/topicmodeling/active', code=307)


def topic_modeling_use_docsim():
    from utils.embed_utils import get_doc_from_tag
    from utils.web_utils import create_doc_display_areas

    new_vector = doc_vec_model.infer_vector(session['document'])
    similar_vectors = doc_vec_model.docvecs.most_similar(positive=[new_vector],
                                                         topn=int(session['topn']))

    # `documents` is a dict such that each key corresponds to a vector and
    # each value is a document. Each key is a tuple of the form:
    # ([corpus, line], similarity) with [corpus, line] being extracted
    # from the document tag returned by similar_vectors.

    documents = {'Corpus: ' + v[0].split("+")[0] +
                 ', Doc #' + v[0].split("+")[1] +
                 ', Similarity: ' + str(v[1])[2:4] + "%":
                 (get_doc_from_tag(v[0]), '') for v in similar_vectors}
    return build_page(contents=create_doc_display_areas(documents),
                      backtarget="/biomed/topicmodeling/use")


def topic_modeling_use_topicsim():
    """ This function creates the page for topic similarity modeling
    """
    return topic_modeling_use_docsim()
