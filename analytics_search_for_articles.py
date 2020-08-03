#!/usr/bin/env python

import mwxml
import mwparserfromhell
import re

dump = mwxml.Dump.from_file(open("cswiki-latest-pages-articles-multistream.xml"))
RE_ANCHOR = re.compile(r'([^#]*)#(.*)')

for linking_page in dump.pages:
    # Sanity: Exclude non-mainpage pages
    if linking_page.namespace != 0:
        continue
    
    # Exclude the main page
    if linking_page.title == "Hlavní strana":
        continue

    print('Processing %s' % linking_page.title)
    revision = next(linking_page) # only current revision should be here
    parsed = mwparserfromhell.parse(revision.text)
    
    # debug
    found_sth = False
    for link in parsed.filter_wikilinks():
        m = RE_ANCHOR.search(str(link.title))
        
        # skip if it's not an anchor link
        if m is None:
            continue
        
        found_sth = True

        linked_page_title = m.group(1)
        linked_page = None
        anchor = m.group(2)

        for candidate_linked_page in dump.pages:
            if candidate_linked_page.title == linked_page_title:
                linked_page = candidate_linked_page
                break
        
        print(linked_page_title)
    
    if found_sth:
        break