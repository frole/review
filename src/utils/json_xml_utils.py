""" This module contains utility functions pertaining to JSON and
    XML processing that may be used accross multiple scripts
"""
import sys; sys.path += ['../']


def add_key_to_JSON(key, value, in_filename, out_filename=None):
    """ Adds a key to every JSON object in a file. Assumes file has one JSON
        object per line. This function alternates between reading and writing
        so it will not work correctly if in_filename == out_filename.
        Arguments:
            - key : the key to add to the JSON objects (must be coercible to str)
            - value : the value corresponding to the key to add to the JSON
                      objects (must be coercible to str)
            - (str) in_filename : name of the file in which to look for JSON objects
            - (str) out_filename : name of the file in which to write updated
                                   JSON objects if left unspecified, defaults
                                   to `in_filename + ".out"`
    """
    import json
    if out_filename is None:
        out_filename = in_filename + ".out"
    with open(in_filename) as f_in:
        with open(out_filename, 'w') as f_out:
            for line in f_in:
                document = json.loads(line)
                document[key] = value
                json.dump(document, f_out)
                print('', file=f_out)


def flatten(tree):
    """ Flattens an XML subtree by removing some nodes such as tables, and extracting the rest of the text into a raw string
        params:
            tree - an XML node / subtree
        return:
            The text in tree as a string containing no XML
    """
    if tree is not None:
        # flattening recursively because grandchild nodes can't be deleted
        children = tree.findall("*")
        for child in children:
            child = flatten(child)
        # blacklist for types of elements that aren't text and that should be removed
        blacklist = ["table", "sup", "xref"]
        for element_type in blacklist:
            for element in list(tree.findall(element_type)):
                if element is not None:
                    # removing each element of each element type on the blacklist
                    tree.remove(element)
        # flattens the remaining tree, appending all the text it finds depth-wise in the tree
        return " ".join(tree.itertext()).replace('\n', ' ').strip()


def xml_to_json(json_dir, xml_dir, json_dataset, label=""):
    """ Will try to parse all XML files in a given directory to extract abstracts,
        full article text, key words, MeSH terms, journal name, title, Pubmed ID,
        and Pubmed Central ID to write to a file as JSON. Each XML file will be
        one line in the final JSON file.
        Arguments:
            - (str) json_dir : the directory in which the JSON file should be written
            - (str) xml_dir : the directory in which to search for the XML files
            - (str) json_dataset : the name of the file the JSON objects should
                                   be written to. May or may not contain the full
                                   path to the file.
            - (str) label : value of the "label" field in the JSON object (defaults
                            to the empty string).
    """
    import re
    import json
    from xml.etree import ElementTree as ET
    from util import flatten
    import traceback
    import os
    from pmc_utils import get_mesh_from_PMID

    error_filename = json_dir + "error.log"
    ferr = open(error_filename, 'w')
    fout = open(json_dataset, 'w')
    j, t, c, d = 0, 0, 0, 0
    # loop over each XML file to extract meaningful data and rewrite as JSON
    for filename in os.listdir(xml_dir):
        if not filename.endswith(".xml"):
            continue
        try:
            # parsing the XML tree
            tree = ET.parse(os.path.abspath(xml_dir + filename))
            # finding all the content of the relevant tags
            journ = tree.findall(".//journal-title")
            title = tree.findall(".//article-title")
            pmid = tree.findall(".//article-id[@pub-id-type='pmid']")
            pmc = tree.findall(".//article-id[@pub-id-type='pmc']")
            abstract_paras = tree.findall(".//abstract//p")
            body_paras = tree.findall(".//body//p")
            kwds = tree.findall(".//kwd")

            abs_text = re.sub(" +", " ",  # replacing multiple spaces with 1 space
                              # flattening and fusing each node
                              " ".join([flatten(p) for p in abstract_paras])).strip()
            body_text = re.sub(" +", " ",
                               " ".join([flatten(p) for p in body_paras])).strip()
            kwds = re.sub(" +", " ",
                          "+".join([flatten(kwd) for kwd in kwds])).strip()
            # title
            try:
                journ = journ[0].text
            except IndexError:
                journ = ""
                j += 1
            try:
                title = title[0].text
            except IndexError:
                title = ""
                t += 1
            try:
                pmc = pmc[0].text
            except IndexError:
                pmc = ""
                c += 1
            try:
                pmid = pmid[0].text
            except IndexError:
                pmid = ""
                d += 1

            meshlist = re.sub(" +", " ",
                              "+".join(get_mesh_from_PMID(pmid))).strip()

            o = {"ab": abs_text, "raw": body_text, "kwds": kwds,
                 "mesh": meshlist, "journ": journ, "title": title,
                 "pmid": pmid, "pmc": pmc, "label": label}

            json.dump(o, fout)
            print('', file=fout)
            # print(json.dumps(o))

        except Exception as e:
            print(filename + str(e), file=ferr)
            traceback.print_exc()

    print((j, t, c, d))

    ferr.close()
    fout.close()
