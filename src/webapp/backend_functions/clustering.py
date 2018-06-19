import sys; sys.path += ['../']; sys.path += ['../../']  # used to import modules from grandparent directory

import random

from async_tasks import coclust_async
from constants import PLOT_FILES_READ
from flask import request
from multiprocessing.pool import Pool
from utils.misc_utils import get_json_dataset_by_name
from utils.web_utils import build_page, corpus_selector  # , make_btn_group

# initializing variables for later
current_coclust_corpus = "test1"

# creating process pool
pool = Pool(processes=2)
# 2nd argument of apply_async is a tuple with args to pass to function
# In this case, on 1-tuple (with a comma to denote tuple-ness)
json_corpus = (get_json_dataset_by_name(current_coclust_corpus),)
# co-clustering can happen in a different process which ignores the GIL
coclusterizer_thread = pool.apply_async(coclust_async, json_corpus)


def clustering_page():
    """ Returns the webpage at <host URL>/biomed/clustering
    """
    global current_coclust_corpus  # These variables are initialized at the top in
    global coclusterizer_thread    # order to start clustering as the app starts
    global pool

    if request.method == 'POST' and request.form["corpus"] != current_coclust_corpus:
        current_coclust_corpus = request.form["corpus"]
        # Arguments of coclust_async are passed as a tuple in the second argument
        # of apply_async. We need a comma to denote a single element tuple.
        # without the comma, apply_async will try to iterate on corpus (str).
        # This applies co clustering with the new corpus.
        pool = Pool(processes=1)
        # json_corpus is a 1-tuple because apply_async takes a tuple as arg
        json_corpus = (get_json_dataset_by_name(request.form["corpus"]),)
        coclusterizer_thread = pool.apply_async(coclust_async, json_corpus)

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
    return build_page(title='Co-clustering results',
                      contents=img_tags,
                      sidebar=options,
                      backtarget="/biomed")
