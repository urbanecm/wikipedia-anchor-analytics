#!/usr/bin/env python

import pymysql
import yaml
import mwxml
import mwparserfromhell
import re

config = yaml.safe_load(open('config.yaml'))

dump = mwxml.Dump.from_file(open("cswiki-latest-pages-articles-multistream.xml"))
RE_ANCHOR = re.compile(r'([^#]*)#(.*)')

connection = pymysql.connect(host=config.get('DB_HOST'),
                             user=config.get('DB_USER'),
                             password=config.get('DB_PASS'),
                             db=config.get('DB_NAME'),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


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

    for link in parsed.filter_wikilinks():
        m = RE_ANCHOR.search(str(link.title))

        if m is not None:
            linked_page_title = m.group(1)
            linked_anchor = m.group(2)
        else:
            continue # comment out if you want no anchor links to be included too
            linked_page_title = str(link.title)
            linked_anchor = None

        with connection.cursor() as cur:
            cur.execute(
                '''
                INSERT INTO link(link_source_page_id, link_source_page_title, link_target_page_title, link_anchor)
                VALUES (%s, %s, %s, %s)
                ''',
                (linking_page.id, linking_page.title, linked_page_title, linked_anchor)
            )
            connection.commit()