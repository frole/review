import sys; sys.path += ['../../']  # used to import modules from grandparent directory
import random

from flask import redirect, request, session
from utils.embed_utils import create_doc_embeddings
from utils.web_utils import TEST_STRING, build_page, corpus_selector, create_doc_display_areas, make_btn_group, make_submit_group

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
    """ Generates the page that shows the top words for each topic
        in the selected corpus at /biomed/topicmodeling/topics
    """
    from utils.topic_utils import get_topic_word_prob
    topic_word_probability = get_topic_word_prob(model=doc_vec_model)

    # Creating the list of tuples to send to create_doc_display_areas
    # Each tuple is of the form (header, document, footer), the headers
    # will be "Topic 1" etc., "documents" are strings of the form:
    #     Aardvark: 89%
    #     Bumblebee: 80%
    # etc., and footers will be empty.
    # We get topics, words and percentages from `topic_word_probability`,
    # and format words and percentages with a `join`ed list comprehension
    # and get the number of the topic by simultaneously iterating over
    # `range(len(topic_word_probability))` thanks to `zip()`.
    topic_top_terms = [(("Topic " + str(i) + ": "),  # head
                        '<br />\n'.join([word + ": " + str(prob * 100)[:5] + "%"
                                         for prob, word in pw_list]),  # doc
                        '')  # footer
                       for i, (_, pw_list) in
                       zip(range(len(topic_word_probability)),
                           topic_word_probability)]

    contents = create_doc_display_areas(documents=topic_top_terms)\
        + make_btn_group(labels=["Proceed"],
                         targets=["/biomed/topicmodeling/use"])

    return build_page(title="Top words per topic",
                      contents=contents)


def topic_modeling_active_learning():
    """ Generates the page for human input for active learning
        at /biomed/topicmodeling/active
        -> use predicted relevant and irrelevant tags to create page
       |   update confirmed relevant and irrelevant tags with user form submission
       |   svm.fit(X=docs, y=relevant)
        -- predicted relevant = svm.predict()
    """
    # express documents as a function of topics
    # {tag: dv[tag] for tag in dv.doctags.keys()}
    from numpy import ones
    from pandas import DataFrame
    from sklearn.svm import LinearSVC
    from utils.web_utils import create_doc_display_areas, create_radio_group

    # placeholder : Further down the line, this method should be an
    # interface for active learning. Maybe make a page specifically
    # for the doc embeddings and then one to access previously
    # created embeddings in order to redirect the user to something
    # else while the computing is happening.
    if "proceed" in request.form:
        from utils.embed_utils import get_doc_from_tag
        from utils.topic_utils import get_top_and_flop_docs_top_sim, get_docs_in_topic_space
        # redirecting with code 307 to ensure redirect uses POST
        return redirect('/biomed/topicmodeling/use/docsim', code=307)
    # In this case, we come from /topicmodeling/use and clicked on the
    # "Active Learning" button, so initialization phase
    if "active" in request.form:
        docs, input_doc = get_docs_in_topic_space(model=doc_vec_model,
                                                  extra_doc=session['document'])
        # predicted relevant and irrelevant tags
        pred_rlvnt_docs_tags, pred_irlvnt_docs_tags =\
            get_top_and_flop_docs_top_sim(n=10,
                                          m=10,
                                          docs_proj=docs,
                                          xtra_doc_proj=input_doc)

        docs = DataFrame(docs)
        session["docs_as_topics"] = docs
        session["svm"] = LinearSVC()
        session["relevant"] = []
        session["irrelevant"] = []
    # case where we're looping
    else:
        for elmt in request.form:
            # if the element is a radio button
            if "radio" in elmt:
                # if the button was checked as "relevant"
                if elmt == 'relevant':
                    # elmt structure is "radio-<DOCTAG>"
                    # elmt.split('-')[1] returns the corresponding doctag
                    # which we add to either the list of relevant or
                    # irrelevant documents as an index
                    session["relevant"].append(
                        doc_vec_model.doctag2index(
                            elmt.split('-')[1]
                        )
                    )
                else:
                    session["irrelevant"].append(
                        doc_vec_model.doctag2index(
                            elmt.split('-')[1]
                        )
                    )
        X = [session["docs_as_topics"][i] for i in session["relevant"] + session["irrelevant"]]
        y = (list(ones(len(session["relevant"]), dtype=int)) +
             list(ones(len(session["irrelevant"]), dtype=int) * 2)
             )
        session["svm"].fit(X=X, y=y)

    # getting documents from tags and putting in a list of tuples
    # for `create_doc_display_areas`
    docs = [("Corpus: " + tag.split('+')[0] + ", Doc #" + tag.split('+')[1],
             get_doc_from_tag(tag),
             create_radio_group(name="radio-" + tag,
                                labels=["Relevant", "Irrelevant"],
                                values=["relevant", "irrelevant"],
                                checked="relevant",
                                form_id="active-form")
             )
            for tag in pred_rlvnt_docs_tags]

    docs += [("Corpus: " + tag.split('+')[0] + ", Doc #" + tag.split('+')[1],
              get_doc_from_tag(tag),
              create_radio_group(name="radio-" + tag,
                                 labels=["Relevant", "Irrelevant"],
                                 values=["relevant", "irrelevant"],
                                 checked="irrelevant",
                                 form_id="active-form")
              )
             for tag in pred_irlvnt_docs_tags]

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

    # `documents` is a list such that each element (a tuple) is of the form
    # `header, document, footer`, where `header` and `footer` are to be
    # displayed above and below the corresponding document respectively.
    # Footers are left empty and headers are of the form
    # "Corpus: <corpusname>, Doc #<docnumber>, Similarity: X%"

    documents = [('Corpus: ' + v[0].split("+")[0] +
                  ', Doc #' + v[0].split("+")[1] +
                  ', Similarity: ' + str(v[1])[2:4] + "%",  # head
                  get_doc_from_tag(v[0]),  # doc
                  '')  # footer
                 for v in similar_vectors]
    return build_page(contents=create_doc_display_areas(documents),
                      backtarget="/biomed/topicmodeling/use")


def topic_modeling_use_topicsim():
    """ This function creates the page for topic similarity modeling
    """
    from utils.embed_utils import get_doc_from_tag
    from utils.topic_utils import get_top_docs_by_topic_sim

    top_docs, top_similarities =\
        get_top_docs_by_topic_sim(n=int(session['topn']),
                                  model=doc_vec_model,
                                  extra_doc_str=session['document'])

    documents = [('Corpus: ' + d.split("+")[0] +
                  ', Doc #' + d.split("+")[1] +
                  ', Similarity: ' + str(s)[2:4] + "%",  # head
                  get_doc_from_tag(d),  # doc
                  '')  # footer
                 for d, s in zip(top_docs, top_similarities)]

    return build_page(contents=create_doc_display_areas(documents),
                      backtarget="/biomed/topicmodeling/use")
