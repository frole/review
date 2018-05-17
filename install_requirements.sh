#!/bin/bash
pip install requirements.txt
# open targets dependencies
pip install spacy textblob unidecode
python -m spacy download en_core_web_md
#pip install https://github.com/d2207197/geniatagger-python/archive/master.zip
