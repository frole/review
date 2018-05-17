import sys; sys.path += ['../']
from coclust.visualization import *
from coclust.coclustering import CoclustMod
from gensim.matutils import corpus2csc
from gensim.corpora import Dictionary
from gensim.models.phrases import Phrases, Phraser
from sentence_generator import Sentences
from constants import CLASSIC3_JSON_DS


class CoClusterizer:
    def __init__(self, dataset=CLASSIC3_JSON_DS):
        # loading the corpus
        corpus = Sentences(dataset)
        # Using a phrase model to refine the corpus
        bigram = Phraser(Phrases(corpus))
        trigram = Phraser(Phrases(bigram[corpus]))
        trig_corpus = trigram[bigram[corpus]]
        self.vocab = list(set([term for doc in trig_corpus for term in doc]))

        # creating standard Dictionary representation of corpus and creating standard doc-term matrix
        dct = Dictionary(trig_corpus)
        bow_corpus = [dct.doc2bow(line) for line in trig_corpus]
        self.doc_term_mat = corpus2csc(bow_corpus).T

    def run_coclust(self):
        # co-clustering
        model = CoclustMod(n_clusters=4)
        model.fit(self.doc_term_mat)  # No errors? Is this right? Gensim types have plug-and-play support?

        top_term_plt = plot_cluster_top_terms(in_data=self.doc_term_mat,
                                              all_terms=self.vocab,
                                              nb_top_terms=5,
                                              model=model,
                                              do_plot=False)

        # print(get_term_graph(X=doc_term_mat,
        #                      model=model,
        #                      terms=vocab,
        #                      n_cluster=2,
        #                      n_top_terms=10,
        #                      n_neighbors=2,
        #                      stopwords=[]))

        clus_sz_plt = plot_cluster_sizes(model=model, do_plot=False)
        mat_plot = plot_reorganized_matrix(X=self.doc_term_mat, model=model, do_plot=False)

        return (top_term_plt, clus_sz_plt, mat_plot)


if __name__ == '__main__':
    cc = CoClusterizer()
    plots = cc.run_coclust()
