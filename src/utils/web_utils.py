TEST_STRING = 'Manifesto on small airway involvement and management in asthma and chronic obstructive pulmonary disease: an Interasma (Global Asthma Association - GAA) and World Allergy Organization (WAO) document endorsed by Allergic Rhinitis and its Impact on Asthma (ARIA) and Global Allergy and Asthma European Network'


def build_page(title='Title', contents=[], sidebar=[]):
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
    with open('./static/template.html') as template:
        page_lines = []
        for line in template:
            if "[CONTENTS]" in line:
                page_lines += '\n'.join(contents)
            elif "[SIDEPANEL]" in line:
                page_lines += '\n'.join(sidebar)
            elif "[TITLE]" in line:
                page_lines += title
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
