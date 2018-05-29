TEST_STRING = 'Manifesto on small airway involvement and management in asthma and chronic obstructive pulmonary disease: an Interasma (Global Asthma Association - GAA) and World Allergy Organization (WAO) document endorsed by Allergic Rhinitis and its Impact on Asthma (ARIA) and Global Allergy and Asthma European Network'


def build_page(title='Title', contents=[], sidebar=[], backtarget="/"):
    """ This function builds a webpage using the template and taking
        as arguments the HTML elements needed to complete the page.
        Args:
            - (str) title: the title of the page that will appear on tabs
            - (list) contents: list of HTML strings that will be written in the
                               body of the page, each element on its own line
            - (list) sidebar: list of HTML strings that will be written in
                              the sidebar, each element on its own line
        Returns:
            - (str) the contents of the webpage to be displayed
    """
    # each area that is destined to be edited (the contents, sidebar and title)
    # are marked by the name of the area in all caps surrounded with brackets,
    # e.g. [CONTENTS] would denote where the contents should go. Therefore,
    # this function simply iterates over lines in the template, replacing the
    # containing a marker with the intended content.
    backarrow = '<a class="btn btn-dark btn-back" href="' + backtarget + '">➡</a>'
    with open('./static/template.html') as template:
        page_lines = []
        for line in template:
            if "[CONTENTS]" in line:
                page_lines += '\n'.join(contents)
            elif "[SIDEPANEL]" in line:
                page_lines += '\n'.join(sidebar)
            elif "[TITLE]" in line:
                page_lines += title
            elif "[BACKARROW]" in line:
                page_lines += backarrow
            else:
                page_lines += line
    page = ''.join(page_lines)
    return page


def corpus_selector(classes, form_id=None):
    """ returns a corpus selector form
        Arguments:form_id
            - (list<str>) classes: list of classes that the form hould have
            - (str) form_id: value of the id field of the form (optional)
    """
    formheader = '<form method="POST" class="' + ' '.join(classes) + '"'
    if form_id is not None:
        formheader += (' id="' + form_id + '"')
    formheader += '>'
    options = [formheader,
               '<select name="corpus">',
               '<option value="test2">Test 2</option>',
               '<option value="test1">Test 1</option>',
               '<option value="asthma">Asthma</option>',
               '<option value="leukemia">Leukemia</option>',
               '<option value="autism">Autism</option>',
               '<option value="classic3">Classic3</option>',
               '<option value="classic4">Classic4</option>',
               '</select>',
               '<input type="submit" class="btn btn-dark submit" value="Submit"/>',
               '</form>']
    return options


def create_doc_display_areas(documents, classes=[]):
    """ Creates an area in which to display text for each document passed
        as argument. Should be styled with CSS to be scrollable.
        Arguments:
            - (dict<any:str>) documents: a dict with any type coercible
                to str as keys to display above the text boxes and strings
                for values to display in the text boxes
            - (list<str>) classes: list of classes that the element
                should have. Defaults to ["document-display-area"].
    """
    text_area_outer_begin = '<div class="outer-document-display-area">'
    text_area_inner_begin = '<p class="inner-document-display-area ' +\
        ' '.join(classes) + '">\n'
    text_area_inner_end = '\n</p>\n'
    text_area_outer_end = '\n</div><br />'

    return [text_area_outer_begin + str(head) + '<br />' + '\n' +
            text_area_inner_begin + doc + text_area_inner_end +
            footer + text_area_outer_end
            for head, (doc, footer) in documents.items()]


def create_topic_selector(doc_tag, values=[1, 2, 3, 4, 5]):
    """ Super temporary placeholder
    """
    # creating the topic radio buttons for the articles
    # the parentheses are only for splitting over multiple lines elegantly
    return ('<span>' +
            '<input type="radio" name="topic' + doc_tag + '" value="' + str(values[0]) + '" form="active-form" checked> Topic 1  ' +
            '<input type="radio" name="topic' + doc_tag + '" value="' + str(values[1]) + '" form="active-form"> Topic 2  ' +
            '<input type="radio" name="topic' + doc_tag + '" value="' + str(values[2]) + '" form="active-form"> Topic 3  ' +
            '<input type="radio" name="topic' + doc_tag + '" value="' + str(values[3]) + '" form="active-form"> Topic 4  ' +
            '<input type="radio" name="topic' + doc_tag + '" value="' + str(values[4]) + '" form="active-form"> Topic 5  ' +
            '</span>')
