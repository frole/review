import sys; sys.path += ['../']
from sklearn.datasets import fetch_20newsgroups

ng = fetch_20newsgroups()
"""
et ensuite ng.data et ng.target

et NG5, sous-ensemble de NG20 correspondant aux classes :

             'rec.motorcycles',
             'rec.sport.baseball',
             'comp.graphics',
             'sci.space',
             'talk.politics.mideast'
"""
