"""This module contains several regular expressions that match various patterns."""
# PAT at the beginning of each regex name stands for Pattern

# Garbage matcher
# matches any string consisting of only |, <, >, +, *, ^, #, =, and hyphen chains.
# this is to identify patterns like ++<===> ######## <---->^^ which serve no purpose but to clutter the text
PAT_GARBAGE = "(\\|*(--+)*<*>*\\+*\\**\\^*#*=*)*"
# layout hyphenation matcher, typically matches hyphens used as bullet points
PAT_BULLET_HYPHENS = "(\\ -\\ )"
# e-mail address matcher
PAT_EMAIL = "([a-z]*[0-9]*\\.*\\+*)+@([a-z]*[0-9]*\\.*-*)+\\.[a-z]+"
# phone number matcher
PAT_PHONE = "\\+?([0-9](-|\\ )?){9, 11}"
# URL matcher
PAT_URL = "https?\\://(www\\.)?([a-z]*[0-9]*\\.?-?%?)+\\.[a-z]+(/([a-z]*[0-9]*-*.+)*)*/?(\\?([a-z]*[0-9]*\\.?-?%?=?&?_?#?\\:?)+)?"

# https?\://(www\.)?
# ([a-z]*[0-9]*\.?-?%?)+ 			# adress
# \.[a-z]+							# domain name
# (/([a-z]*[0-9]*-*.+)*)*/?			# /stuff/between/slashes/
# (\?([a-z]*[0-9]*\.?-?%?=?)+)?		# request details after ?
