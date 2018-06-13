import sys; sys.path += ['../']; sys.path += ['../../']  # used to import modules from grandparent directory

from async_tasks import ner_async_import
from constants import TAG_CATEGORIES
from flask import request
from multiprocessing.pool import ThreadPool
from utils.web_utils import build_page, TEST_STRING  # , make_btn_group

# creating thread pool
tpool = ThreadPool(processes=1)
# 2nd argument of apply_async is a tuple with args to pass to function
# In this case, the empty tuple is passed to apply_async
# here we do the import in a different thread rather than process because
# processes can't return an import. The import takes a long time because
# numpy does a lot of number crunching. Since this happens outside of the
# GIL, this should still result in improved performance.
ner_importer_thread = tpool.apply_async(ner_async_import, ())


def terminology_request_txt():
    """ Returns the webpage at <host URL>/biomed/terminology
    """
    content = ["<p>",
               '<form method="POST" class="text-area-form" id="text-area-form">'
               '<textarea name="text" rows="10" cols="75">',
               TEST_STRING,
               '</textarea>', '<br/>',
               '<input type="submit" class="btn btn-dark submit" value="Submit" style="align: right;"/>',
               '</form>',
               "</p>"]
    options = ['<div class="checkbox-form">']
    options += ['<label><input type="checkbox" form="text-area-form" name="' +
                category + '" checked/>' + category + '</label>'
                for category in TAG_CATEGORIES]
    options += ['</div>']
    return build_page(contents=content, sidebar=options, backtarget="/biomed")


def terminology_tagged_text():
    """ Returns the webpage at <host URL>/biomed/terminology after a POST request
        (intended to be called when settings in the sidebar are changed)
    """
    from utils.web_utils import create_doc_display_areas

    # the fact that this is called systematically isn't a problem.
    tag_text = ner_importer_thread.get()

    text = request.form['text']
    whitelist = []
    for category in TAG_CATEGORIES:
        try:
            if request.form[category] == 'on':
                whitelist += [category]
        except Exception:  # do nothing if some category isn't listed
            pass
    content = create_doc_display_areas([('Results of text tagging',  # head
                                         tag_text.tag(text, whitelist),  # doc
                                         '')  # footer
                                        ],
                                       classes=["document-display-area",
                                                "container"])
    return build_page(contents=content, backtarget="/biomed/terminology")
