from coclust.coclustering import CoclustMod
from coclust.visualization import *
from gensim.matutils import corpus2csc
from gensim.corpora import Dictionary
from gensim.models.phrases import Phrases, Phraser
import string
import re

# loading the corpus
corpus_file = open("./article_corpus.txt")
# removing punctuation, converting to lower case, removing article separators, loading each line as a seperate document (each abstract, article, and keyword set is its own document)
corpus = [re.sub('[' + string.punctuation + ']', '', line.lower()).split() for line in corpus_file if line.find("***") == -1]
corpus_file.close()

# Using a phrase model to refine the corpus
bigram = Phraser(Phrases(corpus))
trigram = Phraser(Phrases(bigram[corpus]))
trig_corpus = trigram[bigram[corpus]]
vocab = list(set([term for doc in trig_corpus for term in doc]))

# creating standard Dictionary representation of corpus and creating standard doc-term matrix
dct = Dictionary(trig_corpus)
bow_corpus = [dct.doc2bow(line) for line in trig_corpus]
doc_term_mat = corpus2csc(bow_corpus).T

# co-clustering
model = CoclustMod(n_clusters=4)
model.fit(doc_term_mat)  # No errors? Is this right? Gensim types have plug-and-play support?
plot_cluster_top_terms(in_data=doc_term_mat,
                       all_terms=vocab,
                       nb_top_terms=5,
                       model=model)
input()
print(get_term_graph(X=doc_term_mat,
                     model=model,
                     terms=vocab,
                     n_cluster=2,
                     n_top_terms=10,
                     n_neighbors=2,
                     stopwords=[]))
input()
plot_cluster_sizes(model=model)
input()
plot_reorganized_matrix(X=doc_term_mat, model=model)
input()
