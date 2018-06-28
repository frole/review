from NER.BioentityTagger import BioEntityTagger
bet = BioEntityTagger()
tag_whitelist = ['ORGANISM', 'DISEASE', 'GENE', 'DRUG', 'ANATOMY', 'LOC']
tag_blacklist = ['PHENOTYPE', 'HEALTHCARE', 'PROCESS', 'DIAGNOSTICS', 'DISEASEALT']


def tag(text, whitelist=tag_whitelist):
    tags = [tag for tag in bet.tag(text) if tag['category'] in whitelist]

    # removing nested tags
    i = 0
    indices_to_rm = []
    while i < len(tags):
        # skipping current index if we already know we'll remove it
        if i in indices_to_rm:
            continue
        # getting all the tags that start at the same index as the current tag
        tags_that_start_at_same_index = [(j, tags[j]['start'], tags[j]['end'])
                                         for j in range(len(tags))
                                         if tags[j]['start'] == tags[i]['start']]
        # adding all the tags that end before the current tag and
        # start at the same index to the list of tags to remove
        if len(tags_that_start_at_same_index) > 1:
            try:
                indices_to_rm += [tags_that_start_at_same_index[j][0]
                                  for j in range(len(tags_that_start_at_same_index))
                                  if tags_that_start_at_same_index[j][2] <
                                  max([tag[2] for tag in tags_that_start_at_same_index])]
            except IndexError:
                print("There has been an index error for tags_that_start_at_same_index")
                print(tags_that_start_at_same_index)
            finally:
                break

        # getting all the tags that end at the same index as the current tag
        tags_that_end_at_same_index = [(j, tags[j]['start'], tags[j]['end'])
                                       for j in range(len(tags))
                                       if tags[j]['end'] == tags[i]['end']]
        # adding all the tags that start after the current tag and
        # end at the same index to the list of tags to remove
        if len(tags_that_start_at_same_index) > 1:
            indices_to_rm += [tags_that_end_at_same_index[j][0]
                              for j in range(len(tags_that_start_at_same_index))
                              if tags_that_start_at_same_index[j][1] >
                              min([tag[1] for tag in tags_that_start_at_same_index])]
        i += 1

    for i in indices_to_rm:
        del tags[i]

    tag_begin = [tag['start'] for tag in tags]
    tag_ends = [tag['end'] for tag in tags]
    for i in range(len(text), -1, -1):
        try:
            # get the index of the first tag that begins at the current character
            j = tag_begin.index(i)
            # slicing string to insert a mark tag at the current index
            text = text[:i] + '<mark title="' + tags[j]['category'] + '">' + text[i:]
        except ValueError:  # catching the exception thrown by index() if i not in tag_begin
            pass
        try:
            j = tag_ends.index(i)
            text = text[:i] + '</mark>' + text[i:]
        except ValueError:
            pass

    return text

# if tag['category'] not in tag_blacklist
