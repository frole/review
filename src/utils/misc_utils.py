"""This module contains utility functions that may be used accross multiple scripts"""
import sys; sys.path += ['../']


def file_len(fname):
    """ returns the length of the file corresponding to the filename given as argument
        Code by SilentGhost on StackOverflow at https://stackoverflow.com/questions/845058/how-to-get-line-count-cheaply-in-python
    """
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def get_raw_texts(datasetname):
    """ Returns a generator on the raw / full text of articles in the
        dataset specified as argument.
    """
    from constants import KNOWN_DATASETS
    try:
        dataset_json_file = get_json_dataset_by_name(datasetname)
        import json
        with open(dataset_json_file) as f:
            for line in f:
                article = json.loads(line)
                yield article["raw"]

    except KeyError:
        if datasetname.lower() == "reuters":
            pass

        elif datasetname.lower() == "20newsgroups"\
                or datasetname.lower() == "ng20":
            from sklearn.datasets import fetch_20newsgroups
            import re
            newsgroups = fetch_20newsgroups(subset='all')
            for email in newsgroups.data:
                yield re.sub(" +", " ", email.replace('\n', ' ').strip())

        elif datasetname.lower() == "ng5":
            from sklearn.datasets import fetch_20newsgroups
            import re
            categories = ['rec.motorcycles',
                          'rec.sport.baseball',
                          'comp.graphics',
                          'sci.space',
                          'talk.politics.mideast']
            newsgroups = fetch_20newsgroups(subset='all', categories=categories)
            for email in newsgroups.data:
                yield re.sub(" +", " ", email.replace('\n', ' ').strip())

    else:
        raise ValueError("No such known dataset. Known datasets are " +
                         ", ".join(KNOWN_DATASETS))


def get_stopwords(datasetname):
    """ TODO : returns the stopwords associated to the dataset
               name passed as argument.
    """
    if datasetname.lower() == "asthma":
        pass
    elif datasetname.lower() == "classic3":
        pass
    elif datasetname.lower() == "classic4":
        pass
    elif datasetname.lower() == "reuters":
        pass
    elif datasetname.lower() == "20newsgroups"\
            or datasetname.lower() == "ng20":
        pass
    elif datasetname.lower() == "ng5":
        pass


def get_json_dataset_by_name(name):
    """ This function returns the filename of a corpus given its name as argument.
        For example, `get_json_dataset_by_name("asthma")` may return something
        similar to "~/Documents/textmining/data/asthma/json/pmc_asthma.json"
    """
    from constants import ASTHMA_JSON_DS, AUTISM_JSON_DS, LEUKEMIA_JSON_DS,\
        CLASSIC3_JSON_DS, CLASSIC4_JSON_DS, TEST1_JSON_DS, TEST2_JSON_DS
    corpus_name = name.lower().strip()
    name_to_dataset = {"asthma": ASTHMA_JSON_DS,
                       "autism": AUTISM_JSON_DS,
                       "leukemia": LEUKEMIA_JSON_DS,
                       "classic3": CLASSIC3_JSON_DS,
                       "classic4": CLASSIC4_JSON_DS,
                       "classic": CLASSIC4_JSON_DS,
                       "test1": TEST1_JSON_DS,
                       "test2": TEST2_JSON_DS
                       }
    return name_to_dataset[corpus_name]


def get_w2v_model_by_name(name):
    """ This function returns the filename of a w2v model given the name
        of its corresponding corpus as argument. For example,
        `get_w2v_model_by_name("asthma")` may return something similar
        to "~/Documents/textmining/data/models/asthma_model.w2v"
    """
    from constants import ASTHMA_W2V_PKL, AUTISM_W2V_PKL, LEUKEMIA_W2V_PKL,\
        CLASSIC3_W2V_PKL, CLASSIC4_W2V_PKL, TEST1_W2V_PKL, TEST2_W2V_PKL
    corpus_name = name.lower().strip()
    name_to_model = {"asthma": ASTHMA_W2V_PKL,
                     "autism": AUTISM_W2V_PKL,
                     "leukemia": LEUKEMIA_W2V_PKL,
                     "classic3": CLASSIC3_W2V_PKL,
                     "classic4": CLASSIC4_W2V_PKL,
                     "classic": CLASSIC4_W2V_PKL,
                     "test1": TEST1_W2V_PKL,
                     "test2": TEST2_W2V_PKL
                     }
    return name_to_model[corpus_name]


def get_vocab(corpusname):
    """ Returns the `set` of words (alphanumeric strings) present
        in a corpus specified as argument.
        Arguments:
            - (str) corpusname: name of the dataset from which
                                 to extract the vocabulary
        Returns:
            - (set) vocab: the vocabulary in the corpus
    """
    import re
    import string
    import json

    # regex containing all punctution
    punct_regex = '[' + string.punctuation + ']'
    corpusfile = get_json_dataset_by_name(corpusname)
    # initailizing vocabulary set
    vocab = set()
    with open(corpusfile) as corpus:
        for article_as_json in corpus:
            article = json.loads(article_as_json)
            try:
                # removing punctuation, converting to lower case,
                # removing article separators, loading each line
                # as a seperate document
                sentence = re.sub(punct_regex, '', article["ab"].lower()).split()
                # vocab becomes the union of vocab and `sentence`
                vocab |= set(sentence)
            except KeyError:  # ignore if article has no abstract
                pass
            vocab |= set(re.sub(punct_regex, '', article["raw"].lower()).split())
    return vocab


def load_google_news(enable_print=True):
    """ Loads the google news word2vec model
        Arguments:
            - (bool) enable_print: if True, will print status messages to
                                   stdout. Defaults to True.
        Returns:
            - (KeyedVectors) model: the google news w2v model
    """
    from gensim.models.keyedvectors import KeyedVectors
    from constants import GOOGLE_NEWS
    if enable_print:
        print("Loading Google News pretrained model...")
    # Load Google's pre-trained Word2Vec model.
    return KeyedVectors.load_word2vec_format(GOOGLE_NEWS, binary=True)


def load_glove(enable_print=True):
    """ Loads the GloVe word2vec model
        Arguments:
            - (bool) enable_print: if True, will print status messages to
                                   stdout. Defaults to True.
        Returns:
            - (KeyedVectors) model: the GloVe w2v model
    """
    from gensim.models.keyedvectors import KeyedVectors
    from constants import GLOVE
    if enable_print:
        print("Loading GloVe model...")
    # Charger le nouveau fichier qui constitue un modele
    return KeyedVectors.load_word2vec_format(GLOVE)


def get_oov_rate(corpusname, modelname="google"):
    """ Finds the OOV (Out Of Vocabulary) rate of a corpus and a model,
        i.e. the proportion of words in the corpus that are unknown in
        the model.
        Arguments:
            - (str) corpusname: name of the corpus to use
            - (str) modelname: name of the model to use
        Returns:
            - (float) oov_rate: number of OOV words / vocab length
    """
    vocab = get_vocab(corpusname)

    if "google" in modelname.lower():
        model = load_google_news()
    elif "glove" in modelname.lower():
        model = load_glove()
    else:
        raise ValueError('unknown model name, known model \
                            names are "google" and "GloVe"')
    return len(vocab - set(model.vocab.keys())) / len(vocab)


def tag_corpus(corpusname,
               tag_whitelist=['ORGANISM',
                              'DISEASE',
                              'GENE',
                              'DRUG',
                              'ANATOMY',
                              'LOC'],
               tag_blacklist=['PHENOTYPE',
                              'DISEASEALT',
                              'HEALTHCARE',
                              'PROCESS',
                              'DIAGNOSTICS']):
    import sys; sys.path += ['../']
    from NER.BioentityTagger import BioEntityTagger
    import json

    corpusfile = get_json_dataset_by_name(corpusname)
    bet = BioEntityTagger()

    with open(corpusfile) as f:
        for line in f:
            article = json.loads(line)
            tags = [tag for tag in bet.tag(article["raw"])
                    if tag['category'] not in tag_blacklist]
            break

    i = 0
    while i < len(tags):
        # finding all the items that start at the same index as some other
        ends_of_tags_that_start_at_same_index = \
            [tag['end'] for tag in tags if tag['start'] == tags[i]['start']]
        # deleting the current tag if it ends after another tag that starts at the same index
        # this means deleting tags that contain others
        if tags[i]['end'] > min(ends_of_tags_that_start_at_same_index):
            del tags[i]
    tags[0].keys()
