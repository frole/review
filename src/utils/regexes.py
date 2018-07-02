"""This module contains several regular expressions that match various patterns."""
# PAT at the beginning of each regex name stands for Pattern

# Garbage matcher
# matches any string consisting of only |, <, >, +, *, ^, #, =, and hyphen chains.
# this is to identify patterns like ++<===> ######## <---->^^ which serve no purpose but to clutter the text
PAT_GARBAGE = r"(\||(--+)|<|>|\+|\*|\^|#|=)*"
# layout hyphenation matcher, typically matches hyphens used as bullet points
PAT_BULLET_HYPHENS = r"(\ -\ )"
# e-mail address matcher
# the theoretical character limit for top-level domains is 63 characters
PAT_EMAIL = r"([a-z]|[0-9]|\.|\+)+@([a-z]|[0-9]|\.|-)+\.[a-z]{2,63}"
# phone number matcher
PAT_PHONE = r"\+?([0-9](-|\ )?){9, 11}"
# URL matcher
PAT_URL = r"https?\://(www\.)?([a-z]|[0-9]|\.|-|%)+\.[a-z]{2,63}(/([a-z]|[0-9]|-|\.|_|#)+)*/?(\?([a-z]|[0-9]|\.|-|%|=|&|_|#|\:|\+)+)?"

# https?\://(www\.)?                            # pretty self explanatory
# ([a-z]|[0-9]|\.|-|%)+                         # adress
# \.[a-z]{2,63}                                 # domain name
# (/([a-z]|[0-9]|-|\.|_|#)+)*/?                 # /stuff/between/slashes/
# (\?([a-z]|[0-9]|\.|-|%|=|&|_|#|\:|\+)+)?"     # request details after ?
