import importlib  # used for asynchronous imports
from constants import PLOT_FILES_WRITE
from articles_coclust import CoClusterizer


def _make_coclusterizer(dataset=None):
    """This function creates a CoClusterizer object.
    This is intended to be run as a separate process because it takes a long time.
    """
    if dataset is not None:
        cc = CoClusterizer(dataset)
    else:
        cc = CoClusterizer()
    return cc


def _make_plots(coclusterizer):
    """This function runs the co-clustering on an initialized
    co-clusterizer and writes the plots to disk as PNG files.
    """
    plots = coclusterizer.run_coclust()
    # for each plot, save as PNG at the path specified in PLOT_FILES_WRITE
    for i in range(len(plots)):
        plots[i].savefig(PLOT_FILES_WRITE[i], format='png')
    print("Coclust plots are ready")
    return plots


def coclust_async(dataset=None):
    """This is the function meant to actually be called as a seperate process,
    calling _make_coclusterizer and _make_plots
    """
    return _make_plots(_make_coclusterizer(dataset))


def ner_async_import():
    tag_text = importlib.import_module('NER.tag_text')
    return tag_text
