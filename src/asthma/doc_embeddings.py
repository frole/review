import sys; sys.path += ['../']
import pickle
import numpy as np
from utils.misc_utils import get_raw_texts, get_stopwords
from constants import DATA_DIR, RESULT_DIR


def save_obj(obj, name):
    with open(DATA_DIR + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(DATA_DIR + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def build_doc_embeddings(tokenized_texts, model):
    """for each text (sequence of tokens) convert it to a sequence of
       w2vec word ids then retrieve the embeddings corresponding to
       these word ids and combine them.
       Also take note of OOV words.

       Args:
          texts (list of lists of tokens): the docs whose embedding vectors
          have to be computed

       Returns:
          a list of couples (doc embedding, oov words for the doc)
          a global dictionary of OOV words
    """
    doc_embeddings_and_oov = []
    oov = {}
    text_idx = 0
    for tokenized_text in tokenized_texts:
        if text_idx % 500 == 0:
            print("text #", text_idx)
        if len(tokenized_text) == 0:
            continue  # should not happen !!!
            # raise Exception ??

        doc_word_indices = []
        tok_not_found = []
        # convert the text to a sequence of word2vec word ids
        for tok in tokenized_text:
            print(tok)
            if tok in model.vocab:
                doc_word_indices.append(model.vocab[tok].index)
            else:
                tok_not_found.append(tok)
                oov[tok] = 1
        text_idx += 1
        # retrieve and combine embeddings and note OOV for the dic
        doc_embedding = np.mean(model.syn0[doc_word_indices], axis=0)
        doc_embeddings_and_oov.append((doc_embedding, tok_not_found))
    return doc_embeddings_and_oov, oov

# save_obj(doc_centroids, "doc_centroids")


dataset_name = "classic3"
stopwords = get_stopwords(dataset_name)
raw_texts = get_raw_texts(dataset_name)  # ou sauvegarde par get_data ?
tokenized_texts = [tokenize(text) for text in raw_texts]
tokenized_filtered_texts = [filter_tokens(tokens, stopwords)
                            for tokens in tokenized_texts]
embeddings, oov = build_doc_embeddings(tokenized_filtered_texts, model)

# A revoir : calcul du chemin pour stocker les résultats d'un
# traitement donne sur un corpus donne.
save_obj(embeddings, DATA_DIR + dataset_name +
         "/" + RESULT_DIR + "embeddigsdoc_embeddings")
