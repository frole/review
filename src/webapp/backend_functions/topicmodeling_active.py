import sys; sys.path += ['../../']  # used to import modules from grandparent directory

from flask import redirect, request, session
from utils.web_utils import build_page, create_doc_display_areas, make_submit_group
from backend_functions.topicmodeling import doc_vec_model

# these dicts are used to save user-specific
# things that can't be stored in sessions
userdata_vectorspace = {}
userdata_classif = {}


class Docvectorspace:
    def __init__(self):
        pass

    def get_docvec_matrix():
        pass


def topic_modeling_active_learning():
    """ Generates the page for human input for active learning
        at /biomed/topicmodeling/active
       +-> use predicted relevant and irrelevant tags to create page
       |   update confirmed relevant and irrelevant tags with user form submission
       |   svm.fit(X=docs, y=relevant)
       +-- predicted relevant = svm.predict()
    """
    import random
    from numpy import ones, argsort
    from pandas import DataFrame
    from sklearn.svm import LinearSVC
    from utils.embed_utils import get_doc_from_tag, kv_indices_to_doctags
    from utils.topic_utils import get_cos_sim, get_top_docs_by_sim
    from utils.web_utils import create_doc_display_areas, create_radio_group

    # proceeding to next page
    if "proceed" in request.form:
        # redirecting with code 307 to ensure redirect uses POST
        return redirect('/biomed/topicmodeling/active/results', code=307)
    # In this case, we come from /topicmodeling/use and clicked on the
    # "Active Learning" button, so initialization phase
    if "active" in request.form:
        session["classifier"] = request.form["classifier"]
        session["vectorspace"] = request.form["vectorspace"]
        n_docs_per_page = int(request.form['n_docs_per_page'])
        # number of relevant and irrelevant documents to
        # display at first iteration of active learning
        n_rlvnt = n_docs_per_page // 2 + n_docs_per_page % 2
        n_irlvnt = n_docs_per_page // 2

        # ==== finding most and least relevant documents ==== #
        # if user selected to represent documents in topic space
        if session["vectorspace"] == "topic":
            from utils.topic_utils import get_docs_in_topic_space
            docs, input_doc = get_docs_in_topic_space(model=doc_vec_model,
                                                      extra_doc=session['document'])
        # if user selected to represent documents in document space
        elif session["vectorspace"] == "document":
            docs = doc_vec_model.docvecs.vectors_docs
            input_doc = doc_vec_model.infer_vector(session['document'])
        else:
            raise ValueError('vectorspace should be "topic" or "document" but is ' +
                             session["vectorspace"])

        doc_similarities = get_cos_sim(input_doc, docs)
        # predicted relevant and irrelevant tags
        pred_rlvnt_docs_tags, _ =\
            get_top_docs_by_sim(n=n_rlvnt,
                                model=doc_vec_model,
                                doc_similarities=doc_similarities)
        pred_irlvnt_docs_tags, _ =\
            get_top_docs_by_sim(n=n_irlvnt,
                                model=doc_vec_model,
                                doc_similarities=doc_similarities,
                                reverse=True)

        # ==== Setting up session ==== #
        # creating a user id and putting it in the session to be able to
        # store things on a per-user basis even when not serializable
        # like datasets and models
        userid = random.randint(0, 65535)
        session['user'] = userid

        # use docs.loc[r, c] to access values
        docs = DataFrame(docs)
        userdata_vectorspace[userid] = docs
        userdata_classif[userid] = LinearSVC(dual=False)

        session["relevant"] = []
        session["irrelevant"] = []
        session["n_docs_per_page"] = n_docs_per_page
        proportion_classified = 0

    # case where we're looping
    else:
        # loading user-specific topic space
        docs = userdata_vectorspace[session['user']]

        for elmt in request.form:
            # if the element is a radio button
            if "radio" in elmt:
                # if the button was checked as "relevant"
                if request.form[elmt] == 'relevant':
                    # elmt structure is "radio-<DOCTAG>"
                    # elmt.split('-')[1] returns the corresponding doctag
                    # which we add to either the list of relevant or
                    # irrelevant documents as an index
                    session["relevant"].append(
                        doc_vec_model.doctag2index[
                            elmt.split('-')[1]
                        ]
                    )
                # if the button was checked as "irrelevant"
                else:
                    session["irrelevant"].append(
                        doc_vec_model.doctag2index[
                            elmt.split('-')[1]
                        ]
                    )
        # Marking session as modified or else changes are not recorded.
        # (it only registers modifications a key is set or deleted)
        # From the documentation:
        #   Be advised that modifications on mutable structures are not
        #   picked up automatically, in that situation you have to
        #   explicitly set the [modified attribute] to True yourself.
        session.modified = True

        # avoiding joining lists every time
        # `relevant` and `irrelevant` may be the prediction made by the topic
        # space model if this is the first iteration or the documents classified
        # manually if this is any other iteration
        classified = session["relevant"] + session["irrelevant"]

        # the proportion of classified documents will be displayed and is
        # used to determine if all documents have already been classified
        proportion_classified = len(classified) / docs.shape[0]
        # if all docs have been classified
        if proportion_classified == 1:
            return redirect('/biomed/topicmodeling/active/results', code=307)

        X = docs.loc[classified, ]
        # The order of `classified` is preserved by `loc`, which means X is
        # split in relevant and irrelevant texts like `classifies` is
        y = (list(ones(len(session["relevant"]), dtype=int)) +
             list(ones(len(session["irrelevant"]), dtype=int) * 2)
             )
        # fitting this user's SVM for the ongoing query
        userdata_classif[session['user']].fit(X=X, y=y)

        # Confidence scores for class "2" where > 0 means this class would
        # be predicted. This is actually the distance to the separation
        # hyperplane, i.e. the farther away a point is form the decision
        # boundary, the more condfident we are.
        prediction = userdata_classif[session['user']].decision_function(docs)

        # indices of sorted prediction
        idx_sorted_pred = argsort(abs(prediction))[::-1]
        # removing documents previously classified
        idx_sorted_pred = [index for index in idx_sorted_pred
                           if index not in classified]

        # keeping only the top n_docs_per_page most certain or
        # whatever's left if there are less than n_docs_per_page
        nsamples = min(len(idx_sorted_pred), session["n_docs_per_page"])
        idx_sorted_pred = idx_sorted_pred[:nsamples]

        # predicted relevant docs are the ones in idx_sorted_pred
        # such that their distance to the decision frontier is
        # positive ("right side" of the frontier)
        pred_rlvnt_docs_tags =\
            kv_indices_to_doctags(keyedvectors=doc_vec_model.docvecs,
                                  indexlist=[i for i in idx_sorted_pred
                                             if prediction[i] > 0])
        # predicted irrelevant docs are the ones in idx_sorted_pred
        # such that their distance to the decision frontier is
        # negative ("wrong side" of the frontier)
        pred_irlvnt_docs_tags =\
            kv_indices_to_doctags(keyedvectors=doc_vec_model.docvecs,
                                  indexlist=[i for i in idx_sorted_pred
                                             if prediction[i] < 0])

    # getting documents from tags and putting in a list of tuples
    # for `create_doc_display_areas`
    pred_rlvnt_docs_tags = list(pred_rlvnt_docs_tags)
    print(pred_rlvnt_docs_tags)
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
    contents = ["<p>These are the articles in the corpus that we are most\
 confident you will find relevant or irrelevant. Please go through them and\
 select for each one whether you find it relevant or not with the radio\
 buttons. The option we expect to be the right one is already checked. Then,\
 you may repeat this process with the next batch of documents in order to\
 improve the screening process or you may let the documents you haven't\
 verified be screened automatically and view the documents we predict you\
 will find relevant.</p>"]
    contents += doc_display_areas
    contents += ['<form method="POST" class="" id="active-form">']
    contents += make_submit_group(labels=["Next batch", "Go to results"],
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


def topic_modeling_active_results():
    """ TODO: figure out why this never displays anything
        because the model doesn't predict anything before this is called
    """
    from itertools import chain
    from utils.embed_utils import get_doc_from_tag
    from utils.embed_utils import kv_indices_to_doctags
    from numpy import ones, argsort

    # performing last prediction to add to relevant documents
    # getting document embeddings matrix and previously classified documents
    docs = userdata_vectorspace[session['user']]
    classified = session["relevant"] + session["irrelevant"]
    # training classifier on known data
    X = docs.loc[classified, ]
    y = (list(ones(len(session["relevant"]), dtype=int)) +
         list(ones(len(session["irrelevant"]), dtype=int) * 2)
         )
    userdata_classif[session['user']].fit(X=X, y=y)

    # making prediction
    prediction = userdata_classif[session['user']].decision_function(docs)
    # getting row indices of predictions in decreasing order of confidence
    idx_sorted_pred = argsort(prediction)[::-1]
    # getting tags of positive predictions
    predrelevant =\
        kv_indices_to_doctags(keyedvectors=doc_vec_model.docvecs,
                              indexlist=[i for i in idx_sorted_pred
                                         if prediction[i] > 0])

    # getting tags of known relevant documents
    # and concatenating with prediction (with `chain` since these are generators)
    relevant = chain(kv_indices_to_doctags(keyedvectors=doc_vec_model.docvecs,
                                           indexlist=session["relevant"]),
                     predrelevant)

    documents = [('Corpus: ' + d.split("+")[0] +
                  ', Doc #' + d.split("+")[1],  # head
                  get_doc_from_tag(d),  # doc
                  '')  # footer
                 for d in relevant]

    return build_page(contents=create_doc_display_areas(documents),
                      backtarget="/biomed/topicmodeling/use")
