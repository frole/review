import sys; sys.path += ['../../']  # used to import modules from grandparent directory
import random

from flask import request, session, redirect
from utils.web_utils import build_page, corpus_selector, TEST_STRING, make_submit_group
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
        dm = int(request.form['dm'])
        dbow_words = 0
        if ('dbow_words' in request.form and
                request.form['dbow_words'] == 'on'):
            dbow_words = 1
        dm_concat = int(request.form['dm_concat'])

        # creating doc2vec model
        model = create_doc_embeddings(corporanames=[corpus],
                                      dm=dm,
                                      dbow_words=dbow_words,
                                      dm_concat=dm_concat)
        doc_vec_model = model
        # redirecting with code 307 to ensure redirect uses POST
        return redirect('/biomed/topicmodeling/topics', code=307)


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
    return topic_modeling_use_docsim()
