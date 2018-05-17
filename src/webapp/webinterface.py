""" This script launches the FLASK web interface for the project"""
import sys; sys.path += ['../']  # used to import modules from parent directory
import random

from async_tasks import coclust_async
from async_tasks import ner_async_import
from constants import PLOT_FILES_READ
from constants import TAG_CATEGORIES
from flask import Flask
from flask import request
from multiprocessing.pool import ThreadPool
from utils.misc_utils import get_json_dataset_by_name
app = Flask(__name__)

# initializing variable for later
current_coclust_corpus = "test1"

pool = ThreadPool(processes=2)
# 2nd argument is a tuple with args to pass to function
# In this case, on 1-tuple (with a comma to denote tuple-ness)
coclusterizer_thread = pool.apply_async(coclust_async,
                                        (get_json_dataset_by_name(current_coclust_corpus),))
# In this case, the empty tuple
ner_importer_thread = pool.apply_async(ner_async_import, ())


def build_page(title='Title', contents=[], sidebar=[]):
    """ This function builds a webpage using the template and taking
        as arguments the HTML elements needed to complete the page.
        Args:
            - (str) title: the title of the page that will appear on tabs
            - (list) contents: list of HTML strings that will be written in the
                               body of the page, each element on its own line
            - (list) sidebar: list of HTML strings that will be written in
                              the sidebar, each element on its own line
        Returns:
            - (str) the contents of the webpage to be displayed
    """
    # each area that is destined to be edited (the contents, sidebar and title)
    # are marked by the name of the area in all caps surrounded with brackets,
    # e.g. [CONTENTS] would denote where the contents should go. Therefore,
    # this function simply iterates over lines in the template, replacing the
    # containing a marker with the intended content.
    with open('./static/template.html') as template:
        page_lines = []
        for line in template:
            if "[CONTENTS]" in line:
                page_lines += '\n'.join(contents)
            elif "[SIDEBAR]" in line:
                page_lines += '\n'.join(sidebar)
            elif "[TITLE]" in line:
                page_lines += title
            else:
                page_lines += line
    page = ''.join(page_lines)
    return page


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
               '<a class="btn btn-dark" href="/biomed/resume" role="button">Résumé</a>',
               '<a class="btn btn-dark" href="/biomed/clustering" role="button">Clustering / Co-clustering</a>',
               '<a class="btn btn-dark" href="/biomed/terminologie" role="button">Terminologie</a>',
               '</p>']
    return build_page(title="Biomedical", contents=buttons)


@app.route("/biomed/resume")
def resume():
    """ Returns the webpage at <host URL>/biomed/resume
    """
    return build_page(title="placeholder")


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
        pool = ThreadPool(processes=1)
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
    options = ['<form method="POST" class="coclust-form checkbox-form">',
               '<select name="corpus">',
               '<option value="test2">Test 2</option>',
               '<option value="test1">Test 1</option>',
               '<option value="asthma">Asthma</option>',
               '<option value="leukemia">Leukemia</option>',
               '<option value="autism">Autism</option>',
               '<option value="classic3">Classic3</option>',
               '<option value="classic4">Classic4</option>',
               '</select>',
               '<input type="submit" class="btn btn-dark submit" value="Submit"/>',
               '</form>']
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
    options += ['<label><input type="checkbox" form="text-area-form" name="' + category + '" checked/>' + category + '</label>' for category in TAG_CATEGORIES]
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
