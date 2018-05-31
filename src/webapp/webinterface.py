""" This script launches the FLASK web interface for the project"""
import sys; sys.path += ['../']  # used to import modules from parent directory

from backend_functions import terminology, topicmodeling, clustering
from flask import Flask
from utils.web_utils import build_page, make_btn_group
app = Flask(__name__)


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
    return build_page(title="placeholder")


@app.route("/biomed")
def biomedical():
    """ Returns the webpage at <host URL>/biomed
    """
    buttons = make_btn_group(labels=["Summary",
                                     "Clustering / Co-clustering",
                                     "Terminology",
                                     "Topic Modeling"],
                             targets=["/biomed/summary",
                                      "/biomed/clustering",
                                      "/biomed/terminology",
                                      "/biomed/topicmodeling"])
    return build_page(title="Biomedical", contents=buttons)


@app.route("/biomed/summary")
def summary():
    """ Returns the webpage at <host URL>/biomed/summary
    """
    return build_page(title="placeholder", backtarget="/biomed")


@app.route("/biomed/topicmodeling", methods=['GET', 'POST'])
def topic_modeling():
    """ Returns the webpage at <host URL>/biomed/topicmodeling
    """
    return topicmodeling.topic_modeling()


@app.route("/biomed/topicmodeling/topics", methods=['GET', 'POST'])
def topic_modeling_top_words():
    """ Returns the webpage at <host URL>/biomed/topicmodeling/topics
        Shows the top words for each topic and has a button to redirect
        the user towards the "use model" page.
    """
    button = make_btn_group(labels=["Proceed"],
                            targets=["/biomed/topicmodeling/use"])
    return build_page(title="Top words per topic",
                      contents=button)


@app.route("/biomed/topicmodeling/active", methods=['POST'])
def topic_modeling_active_learning():
    return topicmodeling.topic_modeling_active_learning()


@app.route("/biomed/topicmodeling/use", methods=['GET', 'POST'])
def topic_modeling_use():
    return topicmodeling.topic_modeling_use()


@app.route("/biomed/clustering", methods=['GET', 'POST'])
def clustering_page():
    """ Returns the webpage at <host URL>/biomed/clustering
    """
    return clustering.clustering_page()


@app.route("/biomed/terminology")
def terminology_request_txt():
    """ Returns the webpage at <host URL>/biomed/terminology
    """
    return terminology.terminology_request_txt()


@app.route("/biomed/terminology", methods=['POST'])
def terminology_tagged_text():
    """ Returns the webpage at <host URL>/biomed/terminology after a POST request
        (intended to be called when settings in the sidebar are changed)
    """
    return terminology.terminology_tagged_text()
