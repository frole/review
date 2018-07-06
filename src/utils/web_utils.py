from jinja2 import Template
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
    with open('./static/template.html', 'r') as templatefile:
        template = Template(templatefile.read())
    page = template.render(contents='\n'.join(contents),
                           sidepanel='\n'.join(sidebar),
                           title=title,
                           backarrow=backarrow)
    return page


def corpus_selector(classes, form_id=None):
    """ returns a corpus selector form (dropdown menu)
        Arguments:
            - (list<str>) classes: list of classes that the form should have
            - (str) form_id: value of the id field of the form (optional)
    """
    formheader = '<form method="POST" class="' + ' '.join(classes) + '"'
    if form_id is not None:
        formheader += (' id="' + form_id + '"')
    formheader += '>'
    options = [formheader] +\
        create_selector(entries=[("test2", "Test 2"),
                                 ("test1", "Test 1"),
                                 ("asthma", "Asthma"),
                                 ("leukemia", "Leukemia"),
                                 ("autism", "Autism"),
                                 ("classic3", "Classic3"),
                                 ("classic4", "Classic4")], name="corpus") +\
        ['<input type="submit" class="btn btn-dark submit" value="Submit"/>',
         '</form>']
    return options


def create_selector(entries, name, form=None):
    """ returns a selector form (dropdown menu)
        Arguments:
            - (list<(str, str)>) entries: list of the form [(value, Text)] for
                each entry where `value` is the internal value for the entry
                and `Text` is the on-screen text for the entry
            - (str) name: name of the element for retrieving values
    """
    if form is not None:
        form_attr = '" form="' + form
    else:
        form_attr = ""
    return ['<select name="' + name + form_attr + '">'] +\
        ['<option value="' + key + '">' + value + '</option>'
         for key, value in entries] +\
        ['</select>']


def create_doc_display_areas(documents, classes=[]):
    """ Creates an area in which to display text for each document passed
        as argument. Should be styled with CSS to be scrollable.
        Arguments:
            - (list<str, str, str>) documents: a list of tuples of the form
                `(header, document, footer)`. The document will be displayed
                in the text boxes, whilst header and footer will be above and
                below the text boxes respectively.
            - (list<str>) classes: list of classes that the element should
                have.
    """
    text_area_outer_begin = '<div class="outer-document-display-area">'
    text_area_inner_begin = '<p class="inner-document-display-area ' +\
        ' '.join(classes) + '">\n'
    text_area_inner_end = '\n</p>\n'
    text_area_outer_end = '\n</div><br />'

    return [text_area_outer_begin + str(head) + '<br />' + '\n' +
            text_area_inner_begin + doc + text_area_inner_end +
            footer + text_area_outer_end
            for (head, doc, footer) in documents]


def create_radio_group(name, labels, values, checked=None, form_id=None):
    """ creates a group of radio buttons.
        Arguments:
            - (str) name: name of the button group
                    (used to group the buttons in the form)
            - (list<str>) labels: one label per button, will be
                    shown on screen
            - (list<str>) values: one value per button, used to
                    retrieve the checked button in a POST request
            - (str) checked: `checked` should be in `values` and designates
                    which button should be checked by default. Lave empty
                    or None if no button should be selected.
            - (str) form_id: the id of the form these buttons should belong
                    to. If None or left blank, the radio group should be
                    inside the form it belongs to.
    """
    # will insert the form parameter if passed as arg
    form = '' if form_id is None else ' form="' + form_id + '"'
    # will append "checked" to the HTML tag of each button for which the
    # label has been specified as needing to be checked in the arguments
    checked_btns = [' checked' if value == checked
                    else '' for value in values]

    group = ['<span>']
    group += ['<input type="radio" name="' + name + '" value="' +
              str(value) + '"' + form + chkstate + '> ' + label
              for label, value, chkstate in
              zip(labels, values, checked_btns)]
    group += ['</span>']
    return '\n'.join(group)


def make_btn_group(labels, targets):
    """ Creates and returns an HTML button group for simple redirections
        Arguments:
            - (list<str>) labels: list of button labels
            - (list<str>) targets: list of URLs the buttons should send to
    """
    buttons = ['<p class="btn-group-lg">']
    buttons += ['<a class="btn btn-dark" href="' + target +
                '" role="button">' + label + '</a>'
                for label, target in zip(labels, targets)]
    buttons += ['</p>']

    return buttons


def make_submit_group(labels, names, form_id=None):
    """ Creates and returns an HTML button group for multiple "submit" buttons
        Arguments:
            - (list<str>) labels: list of button labels
            - (list<str>) names: list of names for the buttons (which identify
                    the pressed button in the request form)
            - (str) form_id: id of the form these buttons belong to. If left
                    blank or None, these buttons should be children of the
                    form element they pertain to.
    """
    formfield = '" form="' + form_id if form_id is not None else ''
    buttons = ['<p class="btn-group-lg">']
    buttons += ['<input type="submit" class="btn btn-dark submit" name="' +
                name + '" value="' + label + formfield + '" />'
                for label, name in zip(labels, names)]
    buttons += ['</p>']
    return buttons
