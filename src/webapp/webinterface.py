""" This script launches the FLASK web interface for the project"""
import sys; sys.path += ['../']  # used to import modules from parent directory
import random

from async_tasks import coclust_async, ner_async_import
from constants import PLOT_FILES_READ, TAG_CATEGORIES
from flask import Flask, request, redirect, url_for
from multiprocessing.pool import Pool
from utils.misc_utils import get_json_dataset_by_name
from utils.web_utils import build_page, corpus_selector
app = Flask(__name__)

# initializing variables for later
current_coclust_corpus = "test1"
doc_embeddings_model = None

pool = Pool(processes=2)
# 2nd argument is a tuple with args to pass to function
# In this case, on 1-tuple (with a comma to denote tuple-ness)
coclusterizer_thread = pool.apply_async(coclust_async,
                                        (get_json_dataset_by_name(current_coclust_corpus),))
# In this case, the empty tuple
ner_importer_thread = pool.apply_async(ner_async_import, ())


@app.route("/")
# each function preceded with @app.route(_path_) is called when _path_ is
# visited and should return the correct webpage as a string
def root():
    """ Returns the webpage at <host URL>/
    """
    buttons = ['<p class="btn-group-lg">',
               '<a class="btn btn-dark" href="/biomed" role="button">Biomedical</a>',
               '<a class="btn btn-dark" href="/patents" role="button">Patents</a>',
               '</p>']
    return build_page(title="Home", contents=buttons)
#    return app.send_static_file('index.html')


@app.route("/patents")
def patents():
    """ Returns the webpage at <host URL>/patents
    """
    return build_page(title="placeholder", contents=["<p>shaz</p><br />" for i in range(1000)])


@app.route("/biomed")
def biomedical():
    """ Returns the webpage at <host URL>/biomed
    """
    buttons = ['<p class="btn-group-lg">',
               '<a class="btn btn-dark" href="/biomed/summary" role="button">Summary</a>',
               '<a class="btn btn-dark" href="/biomed/clustering" role="button">Clustering / Co-clustering</a>',
               '<a class="btn btn-dark" href="/biomed/terminologie" role="button">Terminology</a>',
               '<a class="btn btn-dark" href="/biomed/topic" role="button">Topic Modeling</a>',
               '</p>']
    return build_page(title="Biomedical", contents=buttons)


@app.route("/biomed/summary")
def summary():
    """ Returns the webpage at <host URL>/biomed/summary
    """
    return build_page(title="placeholder")


@app.route("/biomed/topic", methods=['GET', 'POST'])
def topic_modeling():
    """ Returns the webpage at <host URL>/biomed/topic
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
        tag_count = ['<label>Document tag count:',
                     '<input type="text" name="dm_tag_count" form="topic-form" value="1" size="2"/>',
                     '</label>']
        options = ['<div class="checkbox-form">', '']
        options += algorithm + separator
        options += train_wv + separator
        options += context_representation + separator
        options += tag_count
        options += ['</div>']
        return build_page(title="Topic Modeling", contents=selector, sidebar=options)

    elif request.method == 'POST':
        from utils.embed_utils import create_doc_embeddings
        global doc_embeddings_model

        # getting all form elements to send as arguments to doc2vec
        corpus = request.form['corpus']
        dm = int(request.form['dm'])
        dbow_words = 0
        if 'dbow_words' in request.form and request.form['dbow_words'] == 'on':
            dbow_words = 1
        dm_concat = int(request.form['dm_concat'])
        dm_tag_count = int(request.form['dm_tag_count'])
        model = create_doc_embeddings(corporanames=[corpus],
                                      dm=dm,
                                      dbow_words=dbow_words,
                                      dm_concat=dm_concat,
                                      dm_tag_count=dm_tag_count)
        doc_embeddings_model = model
        return redirect('/biomed/topic/active', code=307)

    else:
        return "something went terribly wrong"


@app.route("/biomed/topic/active", methods=['POST'])
def topic_modeling_active_learning():

    # placeholder : for now this method displays the model's
    # methods. Further down the line, it should be an interface
    # for active learning. It should also take more arguments
    # to condition the document embeddings creation.
    # Maybe make a page specifically for the doc embeddings
    # and then one to access previously created embeddings
    # in order to redirect the user to something else while
    # the computing is happening.

    return build_page(title="Topic Modeling", contents=[])


@app.route("/biomed/topic/")
def topic_modeling_use():
    pass


@app.route("/biomed/clustering")
def clustering(corpus=None):
    """ Returns the webpage at <host URL>/biomed/clustering
    """
    global current_coclust_corpus  # These variables are initialized at the top in
    global coclusterizer_thread    # order to start clustering as the app starts
    global pool

    # Corpus is not None <=> function is called after a POST request potentially
    # (but not necessarily) changing the corpus to do clustering on.
    if corpus is not None and corpus != current_coclust_corpus:
        current_coclust_corpus = corpus
        # Arguments of coclust_async are passed as a tuple in the second argument
        # of apply_async. We need a comma to denote a single element tuple.
        # without the comma, apply_async will try to iterate on corpus (str).
        # This applies co clustering with the new corpus.
        pool = Pool(processes=1)
        coclusterizer_thread = pool.apply_async(coclust_async,
                                                (get_json_dataset_by_name(corpus),))

    # we don't actually need the return value, as the plots are written to files.
    # nevertheless, this will force waiting for the thread to finish custering.
    coclusterizer_thread.wait()
    coclusterizer_thread.get()

    # generating random number to concatenate with
    # image filenames to prevent caching
    rng = random.randint(0, 65535)

    begin_img_tag = '<img src="'
    end_img_tag = '">'
    img_tags = ['<p class="img-grp">']
    img_tags += [begin_img_tag + plot_fname + '?' + str(rng) + end_img_tag
                 for plot_fname in PLOT_FILES_READ]
    img_tags += ["</p>"]
    options = corpus_selector(classes=["coclust-form", "checkbox-form"])
    return build_page(contents=img_tags, sidebar=options)


@app.route("/biomed/clustering", methods=['POST'])
def clustering_post():
    """ Returns the webpage at <host URL>/biomed/clustering after a POST request
        (intended to be called when settings in the sidebar are changed)
    """
    corpus = request.form['corpus']
    return clustering(corpus)


@app.route("/biomed/terminologie")
def terminologie_request_txt():
    """ Returns the webpage at <host URL>/biomed/terminologie
    """
    content = ["<p>",
               '<form method="POST" class="text-area-form" id="text-area-form">'
               '<textarea name="text" rows="10" cols="75">',
               'Manifesto on small airway involvement and management in asthma and chronic obstructive pulmonary disease: an Interasma (Global Asthma Association - GAA) and World Allergy Organization (WAO) document endorsed by Allergic Rhinitis and its Impact on Asthma (ARIA) and Global Allergy and Asthma European Network',
               '</textarea>', '<br/>',
               '<input type="submit" class="btn btn-dark submit" value="Submit" style="align: right;"/>',
               '</form>',
               "</p>"]
    options = ['<div class="checkbox-form">']
    options += ['<label><input type="checkbox" form="text-area-form" name="' +
                category + '" checked/>' + category + '</label>'
                for category in TAG_CATEGORIES]
    options += ['</div>']
    return build_page(contents=content, sidebar=options)


@app.route("/biomed/terminologie", methods=['POST'])
def terminologie_tagged_text():
    """ Returns the webpage at <host URL>/biomed/terminologie after a POST request
        (intended to be called when settings in the sidebar are changed)
    """
    tag_text = ner_importer_thread.get()  # the fact that this is called systematically isn't a problem.
    text = request.form['text']
    print(request.form)
    whitelist = []
    for category in TAG_CATEGORIES:
        try:
            if request.form[category] == 'on':
                whitelist += [category]
        except Exception:  # do nothing if some category isn't listed
            pass
    content = ['<p class="container text-justify">',
               tag_text.tag(text, whitelist),
               '</p>']
    return build_page(contents=content)
